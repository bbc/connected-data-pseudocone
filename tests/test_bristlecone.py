"""Tests for `Bristlecone` class. Standard exception handling cannot be used in this case due to the decorator
`utils.server_decorators.catch_exceptions` where the exception is caught and used to abort the context with the
appropriate error code; instead, the context object is mocked and the arguments passed to the `abort` method are
inspected. """
from unittest.mock import MagicMock, patch

import pytest
from grpc import StatusCode
from requests import HTTPError

from app.bristlecone import Bristlecone
from app.services import bristlecone_pb2


@patch('app.bristlecone.UAS_API_KEY', new=None)
def test_init_no_api_key_fail():
    with pytest.raises(ValueError):
        Bristlecone()


class MockRequest:
    user = MagicMock
    limit = 500
    offset = 0

    def __init__(self, user_cookie='', user_id=''):
        self.user.cookie = user_cookie
        self.user.id = user_id


@patch('app.bristlecone.UAS_API_KEY', new='')
def test_list_interactions_no_params():
    bristlecone = Bristlecone()

    mock_request = MockRequest()

    mock_context = MagicMock()

    bristlecone.ListInteractions(mock_request, mock_context)

    code, _ = mock_context.abort.call_args

    assert code[0] == StatusCode.INTERNAL
    assert code[1] == '[BRISTLECONE:ValueError] User cookie or ID must be included in request.'


@patch('app.bristlecone.UAS_API_KEY', new='')
def test_list_interactions_user_id_not_implemented():
    bristlecone = Bristlecone()
    mock_request = MockRequest(user_id='user_id')

    mock_context = MagicMock()

    bristlecone.ListInteractions(mock_request, mock_context)

    code, _ = mock_context.abort.call_args

    assert code[0] == StatusCode.INTERNAL
    assert code[1] == '[BRISTLECONE:NotImplementedError] Offline scoring not yet implemented, so no use for user ID ' \
                      'parameter.'


# test catch auth fail exception

# test catch bad host exception

@patch('app.bristlecone.UAS_API_KEY', new='')
@patch('app.bristlecone.UASClient.get_activity_history')
def test_list_interaction_catch_unauthenticated(mock_uasclient_get_activity_history):
    mock_error_response = MagicMock()
    mock_error_response.status_code = 401
    mock_uasclient_get_activity_history.side_effect = HTTPError(response=mock_error_response)

    bristlecone = Bristlecone()
    mock_request = MockRequest(user_cookie='cookie')
    mock_context = MagicMock()

    bristlecone.ListInteractions(mock_request, mock_context)
    code, _ = mock_context.abort.call_args

    assert code[0] == StatusCode.UNAUTHENTICATED
    assert "[BRISTLECONE:HTTPError]" in code[1]


@pytest.mark.integration
@patch('app.bristlecone.UAS_API_KEY', new='')
def test_healthcheck():
    bristlecone = Bristlecone()
    mock_request = MagicMock()
    mock_context = MagicMock()

    response = bristlecone.HealthCheck(mock_request, mock_context)

    assert response == bristlecone_pb2.Empty()


@patch('app.bristlecone.UAS_API_KEY', new='')
@patch('app.bristlecone.UAS_HOST', new='http://bad_host')
def test_healthcheck_fail():
    bristlecone = Bristlecone()
    mock_request = MagicMock()
    mock_context = MagicMock()

    bristlecone.HealthCheck(mock_request, mock_context)
    code, _ = mock_context.abort.call_args

    assert code[0] == StatusCode.UNAVAILABLE
    assert "[BRISTLECONE:ConnectionError]" in code[1]