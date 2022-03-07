import logging
from typing import Dict, List
import requests
import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class LivestormClient(object):
    BASE_URL = "https://api.livestorm.co/v1"

    def __init__(self, token) -> None:
        self.token = token

    def headers(self):
        return {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "Authorization": self.token,
        }

    def sessions(self, event_id):
        url = f"{self.BASE_URL}/events/{event_id}/sessions"  # ?filter[status]=past
        response = requests.get(url, headers=self.headers())
        logging.debug(json.dumps(response.json()))
        sessions = response.json().get("data", [])
        return sessions

    def session_people(self, session_id):
        url = f"{self.BASE_URL}/sessions/{session_id}/people"
        response = requests.get(url, headers=self.headers())
        logging.debug(json.dumps(response.json()))
        people = response.json().get("data", [])
        return people

    def create_session(
        self, attendees: List, estimated_started_at: datetime, timezone: str
    ) -> Dict:
        url = f"{self.BASE_URL}/events/{event_id}/sessions"
        payload = {
            "data": {
                "type": "sessions",
                "attributes": {
                    "estimated_started_at": estimated_started_at,
                    "timezone": timezone,
                },
                "relationships": {"people": attendees},
            }
        }
        json_payload = json.dumps(payload, cls=DateTimeEncoder)
        logging.debug(json_payload)
        response = requests.post(url, data=json_payload, headers=self.headers())
        logging.debug(json.dumps(response.json()))
        return response.json().get("data", {})

    def delete_session(self, session_id):
        url = f"{self.BASE_URL}/sessions/{session_id}"
        response = requests.delete(url, headers=self.headers())
        response.raise_for_status()
