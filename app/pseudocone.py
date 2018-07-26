import grpc
import logging
import socket
import time

from concurrent import futures
from stackdriver_logging.jsonlog import configure_json_logging

from app import pseudocone_pb2_grpc, pseudocone_pb2
from app.services.database import database_client
from app.settings import ONE_DAY_IN_SECONDS, MAX_WORKERS, GRPC_PORT, DEFAULT_PERMISSABLE_RESOURCE_TYPES, SERVICE_NAME,\
    LOG_LEVEL
from app.utils.log import logger
from app.utils.mapping import convert_json_list_to_pseudocone_response, \
    convert_single_user_interactions_to_proto_response
from app.utils.server_decorators import for_all_methods, log_event, catch_exceptions

# logging
configure_json_logging('bbc-connected-data')
logger = logging.getLogger(SERVICE_NAME)
logging.getLogger(SERVICE_NAME).setLevel(LOG_LEVEL)

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('google.auth.transport.requests').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('b3').setLevel(logging.WARNING)


@for_all_methods(log_event)
@for_all_methods(catch_exceptions)
class Pseudocone(pseudocone_pb2_grpc.PseudoconeServiceServicer):

    def ListTestDataUsers(self, request, context):

        if request.test_period_duration == '':
            raise ValueError("Requests to Pseudocone ListTestDataUsers() endpoint must include the "
                             "'test_period_duration'"
                             " parameter.")

        if request.start_interaction_time == '':
            raise ValueError("Requests to Pseudocone ListTestDataUsers() endpoint must include the "
                             "'start_interaction_time' parameter.")

        if len(request.resource_type) == 0:
            resource_types = DEFAULT_PERMISSABLE_RESOURCE_TYPES
        else:
            resource_types = request.resource_type

        client = database_client(table_name=request.dataset)
        user_data = client.filter_users_with_inclusion_list(request.users, request.limit)
        time_filtered_data = client.filter_interactions_between_dates(iso_start_date=request.start_interaction_time,
                                                                      iso_duration=request.test_period_duration,
                                                                      db_table=user_data)

        filtered_resource_type = client.filter_resource_type(resource_types, db_table=time_filtered_data)
        pseudocone_response = convert_json_list_to_pseudocone_response(filtered_resource_type)
        return pseudocone_response

    def ListInteractions(self, request, context):
        """List user interactions according to the `pseudocone.proto` spec."""

        if request.user.id == '' or request.user == {}:
            raise ValueError('Requests to Pseudocone ListInteractions() endpoint must include the "user" parameter.')

        if request.dataset == '':
            raise ValueError('Requests to Pseudocone ListInteractions() endpoint must include the "dataset"'
                             ' parameter.')

        if request.end_interaction_time == '':
            raise ValueError('Requests to Pseudocone ListInteractions() endpoint must include the '
                             '"end_interaction_time" parameter.')

        if len(request.resource_type) == 0:
            resource_types = DEFAULT_PERMISSABLE_RESOURCE_TYPES
        else:
            resource_types = request.resource_type

        client = database_client(table_name=request.dataset)
        user_interactions = client.filter_users_with_inclusion_list([request.user], user_limit=1)
        time_filtered_data = client.filter_interactions_between_dates(iso_end_date=request.end_interaction_time,
                                                                      iso_duration=request.train_period_duration,
                                                                      db_table=user_interactions)
        filtered_resource_type = client.filter_resource_type(resource_types, db_table=time_filtered_data)
        filtered_with_limit_data = client.limit_num_interactions(request.limit, filtered_resource_type)
        list_interactions_response = convert_single_user_interactions_to_proto_response(filtered_with_limit_data)
        return list_interactions_response

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
