import grpc
import logging
import socket
import time

from concurrent import futures
from stackdriver_logging.jsonlog import configure_json_logging

from app import pseudocone_pb2_grpc, pseudocone_pb2
from app.services.database import DatabaseClient
from app.settings import ONE_DAY_IN_SECONDS, MAX_WORKERS, GRPC_PORT, DEFAULT_PERMISSABLE_RESOURCE_TYPES, PROJECT_NAME

from app.utils.log import logger
from app.utils.mapping import convert_json_list_to_pseudocone_response, \
    convert_single_user_interactions_to_proto_response
from app.utils.server_decorators import for_all_methods, log_event, catch_exceptions

# logging
configure_json_logging(PROJECT_NAME)

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('google.auth.transport.requests').setLevel(logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('b3').setLevel(logging.WARNING)


@for_all_methods(catch_exceptions)
@for_all_methods(log_event)
class Pseudocone(pseudocone_pb2_grpc.PseudoconeServiceServicer):

    def __init__(self):
        self.dataset = None
        self.client = None

    def ListTestDataUsers(self, request, context):

        if not request.test_period_duration:
            err_message = "Requests to Pseudocone ListTestDataUsers() endpoint must include the " \
                          "'test_period_duration' parameter."
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.start_interaction_time:
            err_message = "Requests to Pseudocone ListTestDataUsers() endpoint must include the " \
                          "'start_interaction_time' parameter."
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.resource_type:
            resource_types = DEFAULT_PERMISSABLE_RESOURCE_TYPES
        else:
            resource_types = request.resource_type

        if not self.client or self.dataset != request.dataset:
            # (re)load data if the dataset has changed
            self.dataset = request.dataset
            self.client = DatabaseClient(table_name=request.dataset)

        user_data = self.client.filter_users_with_inclusion_list(request.users, request.limit)
        time_filtered_data = self.client.filter_interactions_between_dates(
            iso_start_date=request.start_interaction_time,
            iso_duration=request.test_period_duration,
            db_table=user_data)

        filtered_resource_type = self.client.filter_resource_type(resource_types, db_table=time_filtered_data)
        pseudocone_response = convert_json_list_to_pseudocone_response(filtered_resource_type)
        return pseudocone_response

    def ListTestDataUsersBetweenDates(self, request, context):

        if not request.end_interaction_time:
            err_message = "Requests to Pseudocone ListTestDataUsersBetweenDates() endpoint must include the " \
                          "'end_interaction_time' parameter."
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.start_interaction_time:
            err_message = "Requests to Pseudocone ListTestDataUsersBetweenDates() endpoint must include the " \
                          "'start_interaction_time' parameter."
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.resource_type:
            resource_types = DEFAULT_PERMISSABLE_RESOURCE_TYPES
        else:
            resource_types = request.resource_type

        if not self.client or self.dataset != request.dataset:
            # (re)load data if the dataset has changed
            self.dataset = request.dataset
            self.client = DatabaseClient(table_name=request.dataset)

        user_data = self.client.filter_users_with_inclusion_list(request.users, request.limit)

        time_filtered_data = self.client.filter_interactions_between_dates(
            iso_start_date=request.start_interaction_time,
            iso_end_date=request.end_interaction_time,
            db_table=user_data)

        filtered_resource_type = self.client.filter_resource_type(resource_types, db_table=time_filtered_data)
        pseudocone_response = convert_json_list_to_pseudocone_response(filtered_resource_type)
        return pseudocone_response

    def ListInteractions(self, request, context):
        """List user interactions according to the `pseudocone.proto` spec."""

        if not request.user.id or not request.user:
            err_message = 'Requests to Pseudocone ListInteractions() endpoint must include the "user" parameter.'
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.end_interaction_time:
            err_message = 'Requests to Pseudocone ListInteractions() endpoint must include the ' \
                          '"end_interaction_time" parameter.'
            logger.exception(err_message)
            raise ValueError(err_message)

        if not request.resource_type:
            resource_types = DEFAULT_PERMISSABLE_RESOURCE_TYPES
        else:
            resource_types = request.resource_type

        if not self.client or self.dataset != request.dataset:
            self.dataset = request.dataset
            self.client = DatabaseClient(table_name=request.dataset)

        user_interactions = self.client.filter_users_with_inclusion_list([request.user], user_limit=1)
        time_filtered_data = self.client.filter_interactions_between_dates(iso_end_date=request.end_interaction_time,
                                                                           iso_duration=request.train_period_duration,
                                                                           db_table=user_interactions)
        filtered_resource_type = self.client.filter_resource_type(resource_types, db_table=time_filtered_data)
        filtered_with_limit_data = self.client.limit_num_interactions(request.limit, filtered_resource_type)

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
