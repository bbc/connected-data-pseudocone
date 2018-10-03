import grpc
import pytest
import random

from unittest.mock import MagicMock, patch, Mock

from app.pseudocone import Pseudocone, create_server
from app import pseudocone_pb2, pseudocone_pb2_grpc
from app.pseudocone_pb2 import ResourceType
from tests.fixtures.database import SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION, \
    SINGLE_USER_SINGLE_ITEM_SINGLE_INTERACTION, \
    SINGLE_USER_ONE_EPISODE_ONE_CLIP


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


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_SINGLE_INTERACTION)
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


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_ONE_EPISODE_ONE_CLIP)
def test_list_test_data_users_with_resource_type(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      resource_type=[ResourceType.Value("CLIP")],
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    response = pseudocone_server["stub"].ListTestDataUsers(request=request)
    assert len(response.items) == 1
    assert response.items[0].user.id == "1"
    assert len(response.items[0].interactions) == 1
    assert response.items[0].interactions[0].pid == "pid2"
    assert response.items[0].interactions[0].uri == "programmes:bbc.co.uk,2018/FIXME/pid2"
    assert response.items[0].interactions[0].activity_time == "2018-03-02T19:53:32.000Z"
    assert response.items[0].interactions[0].completion == "PT11M"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "ended"

    request = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                      users=users,
                                                      resource_type=[ResourceType.Value("EPISODE")],
                                                      start_interaction_time="2018-02-01T00:00:26.318497Z",
                                                      test_period_duration="P0Y1M7DT0H0M0S")

    response = pseudocone_server["stub"].ListTestDataUsers(request=request)
    assert len(response.items) == 1
    assert response.items[0].user.id == "1"
    assert len(response.items[0].interactions) == 1
    assert response.items[0].interactions[0].pid == "pid1"
    assert response.items[0].interactions[0].uri == "programmes:bbc.co.uk,2018/FIXME/pid1"
    assert response.items[0].interactions[0].activity_time == "2018-03-01T19:53:32.000Z"
    assert response.items[0].interactions[0].completion == "P0D"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "started"


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users_multi_interaction(mock_db_data, pseudocone_server):

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
    assert response.items[0].interactions[0].activity_time == "2018-03-01T19:53:32.000Z"
    assert response.items[0].interactions[0].completion == "PT11M"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "ended"


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users_missing_params(mock_db_data, pseudocone_server):

    users = [pseudocone_pb2.UserParam(id="1"), pseudocone_pb2.UserParam(id="2")]
    request_without_start = pseudocone_pb2.ListTestDataUsersRequest(limit=1,
                                                                    users=users,
                                                                    test_period_duration="P0Y1M7DT0H0M0S")

    request_without_duration =\
        pseudocone_pb2.ListTestDataUsersRequest(limit=1, users=users,
                                                start_interaction_time="2018-02-01T00:00:26.318497Z")

    request_without_duration_or_start = \
        pseudocone_pb2.ListTestDataUsersRequest(limit=1, users=users,
                                                start_interaction_time="2018-02-01T00:00:26.318497Z")

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListTestDataUsers(request=request_without_start)

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListTestDataUsers(request=request_without_duration)

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListTestDataUsers(request=request_without_duration_or_start)


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_test_data_users_multi_interaction2(mock_db_data, pseudocone_server):

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
    assert response.items[0].interactions[0].activity_time == "2018-03-01T19:53:32.000Z"
    assert response.items[0].interactions[0].completion == "PT11M"
    assert response.items[0].interactions[0].activity_type == "PLAYS"
    assert response.items[0].interactions[0].action == "ended"


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
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


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_interactions(mock_db_data, pseudocone_server):
    user = pseudocone_pb2.UserParam(id="1")
    request = pseudocone_pb2.ListInteractionsRequest(limit=1,
                                                     user=user,
                                                     resource_type=[pseudocone_pb2.ResourceType.Value("CLIP")],
                                                     end_interaction_time="2018-03-02T00:00:00.318497Z",
                                                     train_period_duration="P0Y0M1DT0H0M0S",
                                                     dataset="dataset")

    response = pseudocone_server["stub"].ListInteractions(request=request)

    assert len(response.interactions) is 1


@patch("app.pseudocone.DatabaseClient.load_data", return_value=SINGLE_USER_SINGLE_ITEM_MULTI_INTERACTION)
def test_list_interactions_missing_params(mock_db_data, pseudocone_server):
    user = pseudocone_pb2.UserParam(id="1")
    request_missing_user = pseudocone_pb2.ListInteractionsRequest(limit=1,
                                                                  end_interaction_time="2018-03-02T00:00:00.318497Z",
                                                                  train_period_duration="P0Y0M1DT0H0M0S")
    request_missing_end = pseudocone_pb2.ListInteractionsRequest(limit=1,
                                                                 user=user,
                                                                 train_period_duration="P0Y0M1DT0H0M0S")
    request_missing_duration =\
        pseudocone_pb2.ListInteractionsRequest(limit=1, end_interaction_time="2018-03-02T00:00:00.318497Z")

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListInteractions(request=request_missing_user)

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListInteractions(request=request_missing_end)

    with pytest.raises(Exception) as error:
        response = pseudocone_server["stub"].ListInteractions(request=request_missing_duration)
