import datetime
import isodate

from app import pseudocone_pb2


def action_context_to_iso8601_duration(action_context):
    """Process the actionContext string to ISO 8601 duration format.

    Example:
        "urn:bbc:tv:version_offset:p05xxtvp#150" -> "PT150"
    """
    if '#' not in action_context:
        return
    duration = action_context.split('#')[-1]
    return isodate.duration_isoformat(datetime.timedelta(seconds=float(duration)))


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
            user_item_interactions = get_data_matching_property(user_data, "resourceid", item_id)
            interaction = extract_earliest_interaction(user_item_interactions)
            user_items.append(convert_db_object_to_interaction_item(interaction))

        user = pseudocone_pb2.UserParam(id=user_id, cookie=None)
        user_interaction_item = pseudocone_pb2.TestDataUser(user=user, interactions=user_items)
        user_interaction_items.append(user_interaction_item)

    return pseudocone_pb2.ListTestDataUsersResponse(items=user_interaction_items)


def extract_earliest_interaction(interactions):

    # Return the earliest interaction
    interactions.sort(key=extract_time, reverse=False)
    return interactions[0]


def extract_time(json):

    return datetime.datetime.strptime(json['activitytime'], "%Y-%m-%dT%H:%M:%S.%fZ")


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
