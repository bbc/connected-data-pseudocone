import datetime

import isodate as isodate

from app.services import bristlecone_pb2


def map_uas_actions_to_proto(uas_actions):
    """Get the activity history and map to protobuf format, see `get_activity_history` for parameters."""
    items = []

    for action in uas_actions:
        item = bristlecone_pb2.InteractionItem(
            action=action['action'],
            activity_time=action['created'],
            activity_type=action['activityType'],
            completion=action_context_to_iso8601_duration(action['actionContext']),
            pid=action['resourceId'],
            uri=pid2uri(action['resourceId'])
        )
        items.append(item)

    uas_actions_proto = bristlecone_pb2.ListInteractionsResponse(
        items=items
    )
    return uas_actions_proto


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
