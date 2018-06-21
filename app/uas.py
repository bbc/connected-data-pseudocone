from urllib.parse import urlparse

import requests

from app.settings import REQUEST_TIMEOUT


class UASClient:
    def __init__(self, api_key, host):
        self.api_key = api_key
        self.host = host
        self.session = self.create_session() 

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "X-API-Key": self.api_key,
            "Host": urlparse(self.host).netloc,
        }
        session = requests.session()
        session.headers.update(headers)
        return session

    def get_activity_history(self, activity, cookie, limit=500, offset=0):
        """
        Fetch from UAS a user's activity history.
        Args:
            activity (str): an activity (eg. plays, reads - more info:
                https://confluence.dev.bbc.co.uk/display/activity/UAS+KPI%27s)
            cookie (str): chkns_atkns cookie
            limit (int): number of actions to return (pagination)
            offset (int): offset of returned results (pagination)
        Returns:
            A list containing all the user history for the given activity.
            Example:
            [
                {
                    "activityType": "plays",
                    "resourceId": "p05xxsmp",
                    "resourceType": "episode",
                    "resourceDomain": "tv",
                    "created": "2018-03-08T13:29:25Z",
                    "action": "paused",
                    "actionContext": "urn:bbc:tv:version_offset:p05xxtvp#150",
                    "@id": "urn:bbc:tv:episode:p05xxsmp"
                }
            ]
        """

        url = f"{self.host}/my/{activity}"
        self.session.headers.update({"Cookie": f"ckns_atkn={cookie}"})
        payload = {
            'startIndex': offset,
            'items': limit
        }
        response = self.session.get(url, params=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()["items"]

    def check_uas_connection(self):
        """Test the connection to UAS, if the expected `tokenNotSupplied` is recieved then the host is not configured
        correctly. """
        response = self.session.get(self.host, timeout=REQUEST_TIMEOUT)
        if response.status_code != 401:
            response.raise_for_status()
