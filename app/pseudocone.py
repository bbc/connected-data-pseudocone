import socket
import time
from concurrent import futures

import grpc

from app.services import bristlecone_pb2_grpc, bristlecone_pb2
from app.uas import UASClient
from app.utils.mapping import map_uas_actions_to_proto
from app.settings import ONE_DAY_IN_SECONDS, MAX_WORKERS, GRPC_PORT, UAS_HOST, UAS_API_KEY
from app.utils.log import logger
from app.utils.server_decorators import for_all_methods, log_event, catch_exceptions


@for_all_methods(log_event)
@for_all_methods(catch_exceptions)
class Bristlecone(bristlecone_pb2_grpc.BristleconeServiceServicer):

    def __init__(self, *_, **__):
        """Set the UAS API key on initiation of this class, this way it is easier to test than if setting it on
        import. """
        super().__init__()
        if UAS_API_KEY is None:
            raise ValueError("Please, set UAS_API_KEY before using the script (currently supports LIVE)")
        self.uas_client = UASClient(UAS_API_KEY, UAS_HOST)

    def ListInteractions(self, request, context):
        """List user interactions according to the `bristlecone.proto` spec."""
        if request.user.cookie == '' and request.user.id == '':
            raise ValueError('User cookie or ID must be included in request.')
        if request.user.id != '':
            raise NotImplementedError('Offline scoring not yet implemented, so no use for user ID parameter.')

        uas_actions = self.uas_client.get_activity_history('plays', request.user.cookie, limit=request.limit,
                                                           offset=request.offset)
        uas_actions_proto = map_uas_actions_to_proto(uas_actions)
        return uas_actions_proto

    def HealthCheck(self, request, context):
        """Send an empty request to UAS and expect a `tokenNotSupplied` response. If successful then return empty,
        if not then catch the exception and abort the context (handled by decorator
        `utils.server_decorators.catch_exceptions`. """
        self.uas_client.check_uas_connection()
        return bristlecone_pb2.Empty()


def serve():  # pragma: no cover
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    bristlecone_pb2_grpc.add_BristleconeServiceServicer_to_server(Bristlecone(), server)
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    server.start()
    addr = f'{socket.gethostname()}:{GRPC_PORT}'
    logger.debug(f'Bristlecone gRPC server started on {addr}.')
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':  # pragma: no cover
    serve()
