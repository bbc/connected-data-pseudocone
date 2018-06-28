"""Tests for `Bristlecone` class. Standard exception handling cannot be used in this case due to the decorator
`utils.server_decorators.catch_exceptions` where the exception is caught and used to abort the context with the
appropriate error code; instead, the context object is mocked and the arguments passed to the `abort` method are
inspected. """
import grpc
import random

from unittest.mock import MagicMock, patch, Mock

import pytest
from grpc import StatusCode
from requests import HTTPError
from tests.fixtures.database import SINGLE_USER_MULTI_ITEM_MULTI_INTERACTION, \
    SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION, \
    SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION, \
    SINGLE_USER_SINGLE_ITEM_SINGLE_INTERACTION, \
    MULTI_USER_MULTI_ITEM_MULTI_INTERACTION

from app.pseudocone import Pseudocone, create_server
from app import pseudocone_pb2, pseudocone_pb2_grpc


@pytest.fixture
def pseudocone_server():
    port = random.randint(6000, 7000)
    server = create_server(port)
    channel = grpc.insecure_channel(f'localhost:{port}')
    stub = pseudocone_pb2_grpc.PseudoconeServiceStub(channel)
    context = Mock()
    pseudocone = Pseudocone()
    response = {
        'server': server,
        'channel': channel,
        'context': context,
        'pseudocone': pseudocone,
        'stub': stub
    }
    yield response
    server.stop(None)


def test_health_check(pseudocone_server):

    response = pseudocone_server["stub"].HealthCheck(pseudocone_pb2.Empty())
    assert response == pseudocone_pb2.Empty()


@patch("app.pseudocone.database_client.load_data", return_value=SINGLE_USER_SINGLE_ITEM_SINGLE_INTERACTION)
def test_list_test_data_users(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    response = pseudocone_server["stub"].ListTestDataUsers(request=request)
    assert len(response.items) == 1
    assert response.items[0].user.id == "1"
    assert len(response.items[0].interactions) == 1
    assert response.items[0].interactions[0].pid == "b09s3kq5"
    assert response.items[0].interactions[0].uri == "programmes:bbc.co.uk,2018/FIXME/b09s3kq5"
    assert response.items[0].interactions[0].activity_time == "2018-03-01T18:53:32.000Z"
    assert response.items[0].interactions[0].completion == "PT11M"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "ended"


@patch("app.pseudocone.database_client.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    response = pseudocone_server["stub"].ListTestDataUsers(request=request)
    assert len(response.items) == 1
    assert response.items[0].user.id == "1"
    assert len(response.items[0].interactions) == 1
    assert response.items[0].interactions[0].pid == "b09s3kq5"
    assert response.items[0].interactions[0].uri == "programmes:bbc.co.uk,2018/FIXME/b09s3kq5"
    assert response.items[0].interactions[0].activity_time == "2018-03-01T18:53:32.000Z"
    assert response.items[0].interactions[0].completion == "P0D"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "started"


@patch("app.pseudocone.database_client.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    response = pseudocone_server["stub"].ListTestDataUsers(request=request)
    assert len(response.items) == 1
    assert response.items[0].user.id == "1"
    assert len(response.items[0].interactions) == 1
    assert response.items[0].interactions[0].pid == "b09s3kq5"
    assert response.items[0].interactions[0].uri == "programmes:bbc.co.uk,2018/FIXME/b09s3kq5"
    assert response.items[0].interactions[0].activity_time == "2018-03-01T18:53:32.000Z"
    assert response.items[0].interactions[0].completion == "P0D"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "started"


@patch("app.pseudocone.database_client.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users_date_format_error(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      start_interaction_time="2018-0201T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListTestDataUsers(request=request)

    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y17DT0H0YM80S")

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListTestDataUsers(request=request)
