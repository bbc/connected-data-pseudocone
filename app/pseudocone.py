import grpc
import socket
import time

from concurrent import futures

from app import pseudocone_pb2_grpc, pseudocone_pb2
from app.services.database import database_client
from app.settings import ONE_DAY_IN_SECONDS, MAX_WORKERS, GRPC_PORT
from app.utils.log import logger
from app.utils.mapping import convert_json_list_to_pseudocone_response
from app.utils.server_decorators import for_all_methods, log_event, catch_exceptions


@for_all_methods(log_event)
@for_all_methods(catch_exceptions)
class Pseudocone(pseudocone_pb2_grpc.PseudoconeServiceServicer):

    def ListTestDataUsers(self, request, context):

        client = database_client(table_name=request.dataset)
        user_data = client.filter_users_with_inclusion_list(request.users, request.limit)
        filtered_data = client.filter_interactions_between_dates(request.start_interaction_time,
                                                                 request.test_period_duration, db_table=user_data)

        pseudocone_response = convert_json_list_to_pseudocone_response(filtered_data)
        return pseudocone_response

    # def ListInteractions(self, request, context):
    #     """List user interactions according to the `pseudocone.proto` spec."""
    #     if request.user.cookie == '' and request.user.id == '':
    #         raise ValueError('User cookie or ID must be included in request.')
    #     if request.user.cookie != '':
    #         raise NotImplementedError('Pseudocone only accepts anonymised BBC hashed IDs.')
    #     uas_actions = self.uas_client.get_activity_history('plays', request.user.cookie, limit=request.limit,
    #                                                        offset=request.offset)
    #     uas_actions_proto = map_uas_actions_to_proto(uas_actions)
    #     return uas_actions_proto

    def HealthCheck(self, request, context):

        return pseudocone_pb2.Empty()


def create_server(port):  # pragma: no cover
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pseudocone_pb2_grpc.add_PseudoconeServiceServicer_to_server(Pseudocone(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    addr = f'{socket.gethostname()}:{port}'
    logger.debug(f'Pseudocone gRPC server started on {addr}.')
    return server


if __name__ == '__main__':  # pragma: no cover
    server = create_server(GRPC_PORT)
    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
