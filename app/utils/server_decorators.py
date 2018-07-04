import grpc
from requests import HTTPError, ConnectionError, ConnectTimeout, RequestException

from app.utils.log import logger


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
            logger.info(err_str)
            context.abort(code, err_str)

    return raise_exception


def log_event(event):
    """Log any requests and responses made to and from the gRPC server."""
    def wrapper(self, request, context):
        logger.debug(f'Request to Pseudocone:\n{request}')
        event_response = event(self, request, context)
        n_res = len(event_response.items) if hasattr(event_response, 'results') else 1
        logger.debug(f'{n_res} results returned from UAS.')
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
