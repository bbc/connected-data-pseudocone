from unittest.mock import MagicMock, patch
import pytest

from app.pseudocone_pb2 import UserParam, ResourceType
from app.services.database import database_client
from tests.fixtures.database import MULTI_USER_MULTI_ITEM_MULTI_INTERACTION, \
                                    SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION, \
                                    MOCK_JSON_LOAD, \
                                    SINGLE_USER_ONE_EPISODE_ONE_CLIP

NUM_INTERACTIONS_USER1 = len([x for x in MULTI_USER_MULTI_ITEM_MULTI_INTERACTION if x["anon_id"] == "1"])
NUM_INTERACTIONS_USER2 = len([x for x in MULTI_USER_MULTI_ITEM_MULTI_INTERACTION if x["anon_id"] == "2"])


@patch("app.services.database.database_client.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_with_inclusion_list(db_data):

    inclusion_list = [UserParam(id="1"), UserParam(id="2")]
    limit = "2"
    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2

    limit = "1"
    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1

    limit = "2"
    inclusion_list = [UserParam(id="1")]
    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1
    assert response[0]["anon_id"] == "1"
    assert response[1]["anon_id"] == "1"
    assert response[2]["anon_id"] == "1"
    assert response[3]["anon_id"] == "1"


@patch("app.services.database.database_client.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_without_inclusion_list(db_data):

    limit = "2"
    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=[], limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2

    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=[], limit=limit, db_table=db_data.return_value)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2


@patch("app.services.database.database_client.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_without_inclusion_list_no_users_available(db_data):

    limit = "2"
    client = database_client()
    response = client.filter_users_with_inclusion_list(inclusion_list=[UserParam(id="na")], limit=limit)
    assert len(response) == 0


@patch("app.services.database.database_client.load_data", return_value=SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION)
def test_filter_interactions_between_dates(db_data):

    # Two item interaction dates for testing here are 1.2018-03-01T19:53:32.000Z; 2. 2018-03-02T19:53:32.000Z

    client = database_client()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P1D"
    filtered_data_single_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                           iso_duration=duration)

    assert len(filtered_data_single_return) == 1
    assert filtered_data_single_return[0]["resourceid"] == "pid1"

    client = database_client()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P2D"
    filtered_data_two_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                        iso_duration=duration)

    assert len(filtered_data_two_return) == 2

    client = database_client()
    start_date = "2018-03-02T00:00:00.000Z"
    duration = "P2D"
    filtered_data_start_duration = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                            iso_duration=duration)

    assert len(filtered_data_start_duration) == 1
    assert filtered_data_start_duration[0]["resourceid"] == "pid2"

    client = database_client()
    end_date = "2018-03-02T00:00:00.000Z"
    duration = "P2D"
    filtered_data_end_duration = client.filter_interactions_between_dates(iso_end_date=end_date, iso_duration=duration)

    assert len(filtered_data_end_duration) == 1
    assert filtered_data_end_duration[0]["resourceid"] == "pid1"

    client = database_client()
    start_date = "2018-03-03T00:00:00.000Z"
    duration = "P2D"
    filtered_data_start_duration_zero_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                                        iso_duration=duration)

    assert len(filtered_data_start_duration_zero_return) == 0

    client = database_client()
    start_date = "2018-03-02T15:53:32.000Z"
    filtered_data_start = client.filter_interactions_between_dates(iso_start_date=start_date)
    assert len(filtered_data_start) == 1
    assert filtered_data_start[0]["resourceid"] == "pid2"

    client = database_client()
    end_date = "2018-03-02T15:53:32.000Z"
    filtered_data_end = client.filter_interactions_between_dates(iso_end_date=end_date)

    assert len(filtered_data_end) == 1
    assert filtered_data_end[0]["resourceid"] == "pid1"


@patch("app.services.database.database_client.load_data", return_value=SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION)
def test_filter_interactions_between_dates_incorrect_params(db_data):

    # Two item interaction dates for testing here are 1.2018-03-01T19:53:32.000Z; 2. 2018-03-02T19:53:32.000Z
    client = database_client()
    start_date = "2018-03-01T00:00:00.000Z"
    end_date = "2018-03-04T00:00:00.000Z"
    duration = "P1D"

    with pytest.raises(Exception) as error:
        filtered_data = client.filter_interactions_between_dates()

    with pytest.raises(Exception) as error:
        filtered_data = client.filter_interactions_between_dates(iso_start_date=start_date, iso_end_date=end_date,
                                                                 iso_duration=duration)


@patch("app.services.database.json.load", return_value=MOCK_JSON_LOAD)
@patch("app.services.database.open", create=True)
def test_load_data(mock_json, mock_file):

    client = database_client()
    assert len(client.table) is 1

    client = database_client(table_name="DB1")
    assert len(client.table) is 1


@patch("app.services.database.json.load", return_value=MOCK_JSON_LOAD)
@patch("app.services.database.open", create=True)
def test_limit_num_interactions(mock_json, mock_file):
        client = database_client()
        data = SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION
        response = client.limit_num_interactions(1, data)
        assert len(response) == 1

        dataNone = None
        response = client.limit_num_interactions(1, dataNone)
        assert response is None


@patch("app.services.database.database_client.load_data", return_value=SINGLE_USER_ONE_EPISODE_ONE_CLIP)
def test_filter_resource_type(db_data):

    client = database_client()
    response = client.filter_resource_type([ResourceType.Value("CLIP"), ResourceType.Value("EPISODE")])
    assert len(response) == 2

    client = database_client()
    response = client.filter_resource_type([ResourceType.Value("CLIP")])
    assert len(response) == 1
    assert response[0]["resourcetype"] == "clip"

    client = database_client()
    response = client.filter_resource_type([ResourceType.Value("EPISODE")])
    assert len(response) == 1
    assert response[0]["resourcetype"] == "episode"


@patch("app.services.database.database_client.load_data", return_value=[])
def test_filter_resource_type_empty_db(db_data):

    client = database_client()
    response = client.filter_resource_type([ResourceType.Value("CLIP")])
    assert len(response) == 0
