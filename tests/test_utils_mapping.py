import pytest

from app.utils.mapping import action_context_to_iso8601_duration, pid2uri

minimal_mock_uas_action = {
    'action': None,
    'created': None,
    'activityType': None,
    'actionContext': None,
    'resourceId': None
}

expected_minimal_response = {
    'items': [
        {
            'action': '',
            'activityTime': '',
            'activityType': '',
            'completion': '',
            'pid': '',
            'uri': ''
        }
    ]
}


@pytest.mark.parametrize('mappings', [
    ('url#0', 'P0D'),
    ('url#10', 'PT10S'),
    ('url#60', 'PT1M'),
    ('url#61', 'PT1M1S'),
    ('url#3600', 'PT1H'),
    ('url#3601', 'PT1H1S'),
    ('url#3661', 'PT1H1M1S'),
    ('url', None),
])
def test_action_context_to_iso8601_duration(mappings):
    assert action_context_to_iso8601_duration(mappings[0]) == mappings[1]


def test_pid2uri():
    assert pid2uri('pid') == "programmes:bbc.co.uk,2018/FIXME/pid"
    assert pid2uri(None) is None
