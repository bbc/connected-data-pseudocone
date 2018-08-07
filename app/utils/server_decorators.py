import grpc
import logging
import socket

from stackdriver_logging.tracing import end_span, start_span

from app.settings import SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)


def catch_exceptions(attempted_func):
    """
    Catch gRPC exceptions and deal with accordingly.

    Error codes: https://grpc.io/grpc/python/grpc.html#grpc.StatusCode
    """
    def raise_exception(self, request, context):
        # todo: log exceptions too
        try:
            return attempted_func(self, request, context)

        except (TypeError, Exception) as e:
            code = grpc.StatusCode.INTERNAL
            logger.exception(e)
            err_str = str(f'[PSEUDOCONE:{e.__class__.__name__}] {e}')

        logger.error(err_str)
        end_span()
        context.abort(code, err_str)
    return raise_exception


def log_event(event):
    """Log any requests and responses made to and from the gRPC server."""
    def wrapper(self, request, context):

        b3_values = getattr(request, 'b3_values', {})
        start_span(b3_values, SERVICE_NAME, event.__name__, socket.gethostname())
        logger.info(f"gRPC - Call '{event.__name__}': {request}")
        event_response = event(self, request, context)
        logger.info(f"gRPC - Return '{event.__name__}'")
        end_span()
        return event_response

    return wrapper


def for_all_methods(decorator):
    """Apply a decorator to all methods of a Class, excluding `__init__`."""
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr != '__init__':
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
