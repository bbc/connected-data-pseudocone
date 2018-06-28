# from unittest.mock import MagicMock, patch
#
# import pytest
# import requests
# from requests import HTTPError
#
# from app.uas import UASClient
# from app.settings import DEFAULT_UAS_HOST
#
#
# def test_client_init():
#     """Test no exception thrown when initialising client."""
#     uasclient = UASClient('', '')
#
#
# @patch('app.uas.requests.Session.get')
# def test_client_get_activity_history_session_headers(mock_session_get):
#     expected_headers = {
#         'User-Agent': 'python-requests/2.18.4',
#         'Accept-Encoding': 'gzip, deflate',
#         'Accept': 'application/json',
#         'Connection': 'keep-alive',
#         'X-API-Key': 'test_api_key',
#         'Host': '',
#         'Cookie': 'ckns_atkn=test_cookie'
#     }
#     uasclient = UASClient('test_api_key', 'test_host')
#     _ = uasclient.get_activity_history('test_activity', 'test_cookie')
#     assert uasclient.session.headers == expected_headers
#
#
# def test_client_get_activity_bad_host_fail():
#     uasclient = UASClient('', 'http://bad_host')
#     with pytest.raises(requests.exceptions.ConnectionError):
#         uasclient.get_activity_history('', '')
#
# def test_client_get_activity_bad_url_fail():
#     uasclient = UASClient('', 'bad_host')
#     with pytest.raises(requests.exceptions.MissingSchema):
#         uasclient.get_activity_history('', '')
#
#
# @pytest.mark.integration
# def test_client_get_activity_bad_cookie_fail():
#     uasclient = UASClient('bad_cookie', DEFAULT_UAS_HOST)
#     with pytest.raises(HTTPError):
#         uasclient.get_activity_history('', '')
#
#
# mock_uas_response = {
#     'other_stuff': {},
#     'items': [
#         {'activityType': 'plays', 'resourceId': 'p05psmxq', 'resourceType': 'clip', 'resourceDomain': 'radio',
#          'created': '2018-03-26T10:32:58Z', 'action': 'paused',
#          'actionContext': 'urn:bbc:radio:version_offset:p05psmxt#2',
#          '@id': 'urn:bbc:radio:clip:p05psmxq'},
#         {'activityType': 'plays', 'resourceId': 'p05ysllr', 'resourceType': 'episode', 'resourceDomain': 'tv',
#          'created': '2018-03-18T23:34:24Z', 'action': 'ended',
#          'actionContext': 'urn:bbc:tv:version_offset:p05ysm2y#1959',
#          '@id': 'urn:bbc:tv:episode:p05ysllr'}
#     ]
# }
#
# expected_get_activity_history_response = mock_uas_response['items']
#
#
# @patch('app.uas.requests.Session.get')
# def test_client_get_activity_history(mock_session_get):
#     uasclient = UASClient('test_api_key', 'test_host')
#
#     mock_response = MagicMock()
#     mock_response.json.return_value = mock_uas_response
#
#     mock_session_get.return_value = mock_response
#
#     response = uasclient.get_activity_history('', '')
#     assert response == expected_get_activity_history_response
#
#
# @pytest.mark.integration
# def test_client_check_uas_connection():
#     uasclient = UASClient('test_api_key', DEFAULT_UAS_HOST)
#     uasclient.check_uas_connection()
#
#
# def test_client_check_uas_connection_bad_host():
#     uasclient = UASClient('test_api_key', 'http://bad_host')
#     with pytest.raises(requests.exceptions.ConnectionError):
#         uasclient.check_uas_connection()
#
#
#
#
#
#
#
