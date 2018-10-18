# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import app.pseudocone_pb2 as pseudocone__pb2


class PseudoconeServiceStub(object):
  """SERVICE

  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ListTestDataUsers = channel.unary_unary(
        '/pseudocone.PseudoconeService/ListTestDataUsers',
        request_serializer=pseudocone__pb2.ListTestDataUsersRequest.SerializeToString,
        response_deserializer=pseudocone__pb2.ListTestDataUsersResponse.FromString,
        )
    self.ListInteractions = channel.unary_unary(
        '/pseudocone.PseudoconeService/ListInteractions',
        request_serializer=pseudocone__pb2.ListInteractionsRequest.SerializeToString,
        response_deserializer=pseudocone__pb2.ListInteractionsResponse.FromString,
        )
    self.ListTestDataUsersBetweenDates = channel.unary_unary(
        '/pseudocone.PseudoconeService/ListTestDataUsersBetweenDates',
        request_serializer=pseudocone__pb2.ListTestDataUsersBetweenDatesRequest.SerializeToString,
        response_deserializer=pseudocone__pb2.ListTestDataUsersBetweenDatesResponse.FromString,
        )
    self.ListReactions = channel.unary_unary(
        '/pseudocone.PseudoconeService/ListReactions',
        request_serializer=pseudocone__pb2.ListReactionsRequest.SerializeToString,
        response_deserializer=pseudocone__pb2.ListReactionsResponse.FromString,
        )
    self.ListFeedbacks = channel.unary_unary(
        '/pseudocone.PseudoconeService/ListFeedbacks',
        request_serializer=pseudocone__pb2.ListFeedbacksRequest.SerializeToString,
        response_deserializer=pseudocone__pb2.ListFeedbacksResponse.FromString,
        )
    self.HealthCheck = channel.unary_unary(
        '/pseudocone.PseudoconeService/HealthCheck',
        request_serializer=pseudocone__pb2.Empty.SerializeToString,
        response_deserializer=pseudocone__pb2.Empty.FromString,
        )


class PseudoconeServiceServicer(object):
  """SERVICE

  """

  def ListTestDataUsers(self, request, context):
    """List of test user objects, each containing a user id and a list of interaction items associated with that user
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListInteractions(self, request, context):
    """For a queried user ID, it returns a corresponding list of interaction items before a given date-time.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListTestDataUsersBetweenDates(self, request, context):
    """
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListReactions(self, request, context):
    """List interaction items, each containing single-user interaction data from UAS about a single media item

    For a queried user ID and list of media item URIs, it returns a corresponding list of interaction items
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListFeedbacks(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def HealthCheck(self, request, context):
    """Health check
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_PseudoconeServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ListTestDataUsers': grpc.unary_unary_rpc_method_handler(
          servicer.ListTestDataUsers,
          request_deserializer=pseudocone__pb2.ListTestDataUsersRequest.FromString,
          response_serializer=pseudocone__pb2.ListTestDataUsersResponse.SerializeToString,
      ),
      'ListInteractions': grpc.unary_unary_rpc_method_handler(
          servicer.ListInteractions,
          request_deserializer=pseudocone__pb2.ListInteractionsRequest.FromString,
          response_serializer=pseudocone__pb2.ListInteractionsResponse.SerializeToString,
      ),
      'ListTestDataUsersBetweenDates': grpc.unary_unary_rpc_method_handler(
          servicer.ListTestDataUsersBetweenDates,
          request_deserializer=pseudocone__pb2.ListTestDataUsersBetweenDatesRequest.FromString,
          response_serializer=pseudocone__pb2.ListTestDataUsersBetweenDatesResponse.SerializeToString,
      ),
      'ListReactions': grpc.unary_unary_rpc_method_handler(
          servicer.ListReactions,
          request_deserializer=pseudocone__pb2.ListReactionsRequest.FromString,
          response_serializer=pseudocone__pb2.ListReactionsResponse.SerializeToString,
      ),
      'ListFeedbacks': grpc.unary_unary_rpc_method_handler(
          servicer.ListFeedbacks,
          request_deserializer=pseudocone__pb2.ListFeedbacksRequest.FromString,
          response_serializer=pseudocone__pb2.ListFeedbacksResponse.SerializeToString,
      ),
      'HealthCheck': grpc.unary_unary_rpc_method_handler(
          servicer.HealthCheck,
          request_deserializer=pseudocone__pb2.Empty.FromString,
          response_serializer=pseudocone__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'pseudocone.PseudoconeService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
