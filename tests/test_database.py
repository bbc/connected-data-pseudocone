from unittest.mock import MagicMock, patch

from app.pseudocone_pb2 import UserParam
import pytest

from app.services.database import database_client
from tests.fixtures.database import MULTI_USER_MULTI_ITEM_MULTI_INTERACTION, \
                                    SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION

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


@patch("app.services.database.database_client.load_data", return_value=SINGLE_USER_MULTI_ITEM_SINGLE_INTERACTION)
def test_filter_interactions_between_dates(db_data):

    # Two item interaction dates for testing here are 1.2018-03-01T19:53:32.000Z; 2. 2018-03-02T19:53:32.000Z

    client = database_client()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P1D"
    filtered_data = client.filter_interactions_between_dates(iso_start_date=start_date, iso_duration=duration)

    assert len(filtered_data) == 1
    assert filtered_data[0]["resourceid"] == "pid1"

    client = database_client()
    start_date = "2018-03-01T00:00:00.000Z"
    duration = "P2D"
    filtered_data = client.filter_interactions_between_dates(iso_start_date=start_date, iso_duration=duration)

    assert len(filtered_data) == 2

    client = database_client()
    start_date = "2018-03-02T00:00:00.000Z"
    duration = "P2D"
    filtered_data = client.filter_interactions_between_dates(iso_start_date=start_date, iso_duration=duration)

    assert len(filtered_data) == 1
    assert filtered_data[0]["resourceid"] == "pid2"
