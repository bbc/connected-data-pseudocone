import os
from unittest.mock import patch

import pytest

from app.pseudocone_pb2 import UserParam, ResourceType
from app.services.database import DatabaseClient
from app.settings import DATA_DUMP_FILE_NAME
from tests.fixtures.database import MULTI_USER_MULTI_ITEM_MULTI_INTERACTION, \
                                    SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION, \
                                    SINGLE_USER_ONE_EPISODE_ONE_CLIP

NUM_INTERACTIONS_USER1 = len([x for x in MULTI_USER_MULTI_ITEM_MULTI_INTERACTION if x["anon_id"] == "1"])
NUM_INTERACTIONS_USER2 = len([x for x in MULTI_USER_MULTI_ITEM_MULTI_INTERACTION if x["anon_id"] == "2"])


@patch("app.services.database.DatabaseClient.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_with_inclusion_list(db_data):

    inclusion_list = [UserParam(id="1"), UserParam(id="2")]
    limit = "2"
    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, user_limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2

    limit = "1"
    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, user_limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1

    limit = "2"
    inclusion_list = [UserParam(id="1")]
    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=inclusion_list, user_limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1
    assert response[0]["anon_id"] == "1"
    assert response[1]["anon_id"] == "1"
    assert response[2]["anon_id"] == "1"
    assert response[3]["anon_id"] == "1"


@patch("app.services.database.DatabaseClient.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_without_inclusion_list(db_data):

    limit = "2"
    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=[], user_limit=limit)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2

    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=[], user_limit=limit,
                                                       db_table=db_data.return_value)
    assert len(response) == NUM_INTERACTIONS_USER1 + NUM_INTERACTIONS_USER2


@patch("app.services.database.DatabaseClient.load_data", return_value=MULTI_USER_MULTI_ITEM_MULTI_INTERACTION)
def test_filter_users_without_inclusion_list_no_users_available(db_data):

    limit = "2"
    client = DatabaseClient()
    response = client.filter_users_with_inclusion_list(inclusion_list=[UserParam(id="na")], user_limit=limit)
    assert len(response) == 0


@patch("app.services.database.DatabaseClient.load_data", return_value=SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION)
def test_filter_interactions_between_dates(db_data):

    # Two item interaction dates for testing here are 1.2018-03-01T19:53:32.000Z; 2. 2018-03-02T19:53:32.000Z

    client = DatabaseClient()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P1D"
    filtered_data_single_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                           iso_duration=duration)

    assert len(filtered_data_single_return) == 1
    assert filtered_data_single_return[0]["resourceid"] == "pid1"

    client = DatabaseClient()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P2D"
    filtered_data_two_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                        iso_duration=duration)

    assert len(filtered_data_two_return) == 2

    client = DatabaseClient()
    start_date = "2018-03-02T00:00:00.000Z"
    duration = "P2D"
    filtered_data_start_duration = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                            iso_duration=duration)

    assert len(filtered_data_start_duration) == 1
    assert filtered_data_start_duration[0]["resourceid"] == "pid2"

    client = DatabaseClient()
    end_date = "2018-03-02T00:00:00.000Z"
    duration = "P2D"
    filtered_data_end_duration = client.filter_interactions_between_dates(iso_end_date=end_date, iso_duration=duration)

    assert len(filtered_data_end_duration) == 1
    assert filtered_data_end_duration[0]["resourceid"] == "pid1"

    client = DatabaseClient()
    start_date = "2018-03-03T00:00:00.000Z"
    duration = "P2D"
    filtered_data_start_duration_zero_return = client.filter_interactions_between_dates(iso_start_date=start_date,
                                                                                        iso_duration=duration)

    assert len(filtered_data_start_duration_zero_return) == 0

    client = DatabaseClient()
    start_date = "2018-03-02T15:53:32.000Z"
    filtered_data_start = client.filter_interactions_between_dates(iso_start_date=start_date)
    assert len(filtered_data_start) == 1
    assert filtered_data_start[0]["resourceid"] == "pid2"

    client = DatabaseClient()
    end_date = "2018-03-02T15:53:32.000Z"
    filtered_data_end = client.filter_interactions_between_dates(iso_end_date=end_date)

    assert len(filtered_data_end) == 1
    assert filtered_data_end[0]["resourceid"] == "pid1"


@patch("app.services.database.DatabaseClient.load_data", return_value=SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION)
def test_filter_interactions_between_dates_incorrect_params(db_data):

    # Two item interaction dates for testing here are 1.2018-03-01T19:53:32.000Z; 2. 2018-03-02T19:53:32.000Z
    client = DatabaseClient()
    start_date = "2018-03-01T00:00:00.000Z"
    end_date = "2018-03-04T00:00:00.000Z"
    duration = "P1D"

    with pytest.raises(Exception):
        client.filter_interactions_between_dates()

    with pytest.raises(Exception):
        client.filter_interactions_between_dates(iso_start_date=start_date, iso_end_date=end_date,
                                                 iso_duration=duration)


@pytest.mark.integration
def test_load_data_from_gcp_file():
    client = DatabaseClient(table_name=DATA_DUMP_FILE_NAME)
    assert len(client.table) == 1000


@patch("app.services.database.gcp_bucket.read_table", return_value=None)
def test_load_data_from_local_file(mock_gcp_read):
    test_file = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_user_data.json')
    client = DatabaseClient(table_name=test_file)
    assert mock_gcp_read.called_once_with(test_file)
    assert isinstance(client.table, list)
    assert len(client.table) == 3


def test_limit_num_interactions():
        test_file = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_user_data.json')
        client = DatabaseClient(table_name=test_file)
        response = client.limit_num_interactions(1, client.table)
        assert len(response) == 1

        dataNone = None
        response = client.limit_num_interactions(1, dataNone)
        assert response is None


@patch("app.services.database.DatabaseClient.load_data", return_value=SINGLE_USER_ONE_EPISODE_ONE_CLIP)
def test_filter_resource_type(db_data):

    client = DatabaseClient()
    response = client.filter_resource_type([ResourceType.Value("CLIP"), ResourceType.Value("EPISODE")])
    assert len(response) == 2

    client = DatabaseClient()
    response = client.filter_resource_type([ResourceType.Value("CLIP")])
    assert len(response) == 1
    assert response[0]["resourcetype"] == "clip"

    client = DatabaseClient()
    response = client.filter_resource_type([ResourceType.Value("EPISODE")])
    assert len(response) == 1
    assert response[0]["resourcetype"] == "episode"


@patch("app.services.database.DatabaseClient.load_data", return_value=[])
def test_filter_resource_type_empty_db(db_data):

    client = DatabaseClient()
    response = client.filter_resource_type([ResourceType.Value("CLIP")])
    assert len(response) == 0
