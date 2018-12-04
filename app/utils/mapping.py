import datetime
import logging

import isodate

from app import pseudocone_pb2
from app.settings import SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)


def action_context_to_iso8601_duration(action_context):
    """Process the actionContext string to ISO 8601 duration format.

    Example:
        "urn:bbc:tv:version_offset:p05xxtvp#150" -> "PT150"
    """
    try:
        duration = action_context.split('#')[-1]
        return isodate.duration_isoformat(datetime.timedelta(seconds=float(duration)))
    except Exception as e:
        logger.exception(e)


def pid2uri(pid):
    """Map a PID to a Datalab URI."""
    if pid is None:
        return
    return "programmes:bbc.co.uk,2018/FIXME/{}".format(pid)


def convert_json_list_to_pseudocone_response(data):

    unique_users_ids = get_unique_vals_for_property(data, "anon_id")
    user_interaction_items = []
    for user_id in unique_users_ids:
        user_data = get_data_matching_property(data, "anon_id", user_id)
        unique_item_ids = get_unique_vals_for_property(user_data, "resourceid")
        user_items = []

        for item_id in unique_item_ids:
            try:
                user_item_interactions = get_data_matching_property(user_data, "resourceid", item_id)
                interaction = extract_latest_interaction(user_item_interactions)
                user_items.append(convert_db_object_to_interaction_item(interaction))
            except Exception as e:
                logger.exception(e)

        user = pseudocone_pb2.UserParam(id=user_id, cookie=None)
        user_interaction_item = pseudocone_pb2.TestDataUser(user=user, interactions=user_items)
        user_interaction_items.append(user_interaction_item)

    return pseudocone_pb2.ListTestDataUsersResponse(items=user_interaction_items)


def convert_single_user_interactions_to_proto_response(data):

    unique_item_ids = get_unique_vals_for_property(data, "resourceid")
    user_items = []

    for item_id in unique_item_ids:
        user_item_interactions = get_data_matching_property(data, "resourceid", item_id)
        interaction = extract_latest_interaction(user_item_interactions)  # would not be necessary with the new dump
        user_items.append(convert_db_object_to_interaction_item(interaction))

    list_interactions_response = pseudocone_pb2.ListInteractionsResponse(interactions=user_items)

    return list_interactions_response


def extract_latest_interaction(interactions):

    # Return the latest interaction
    interactions.sort(key=extract_time, reverse=True)
    return interactions[0]


def extract_time(json):

    return isodate.parse_datetime(json['activitytime']).replace(tzinfo=None)


def get_data_matching_property(data, property, value):

    return [interaction for interaction in data if interaction[property] == value]


def get_unique_vals_for_property(interactions_data, property):

    return list(set([interaction[property] for interaction in interactions_data]))


def convert_db_object_to_interaction_item(obj):

    interaction_item = pseudocone_pb2.InteractionItem(action=obj["action"],
                                                      activity_time=obj["activitytime"],
                                                      activity_type=obj["activitytype"],
                                                      completion=action_context_to_iso8601_duration(
                                                               obj["actioncontext"]),
                                                      pid=obj["resourceid"],
                                                      uri=pid2uri(obj["resourceid"]))

    return interaction_item
