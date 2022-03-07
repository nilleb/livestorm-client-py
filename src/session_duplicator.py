from . import LivestormClient
from typing import Dict
from datetime import datetime, timedelta


class SessionDuplicator(object):
    def __init__(self, client: LivestormClient, event_id: str) -> None:
        self.client = client
        self.event_id = event_id

    def extract_team_members(self, session_id):
        people = self.client.session_people(session_id)
        for person in people:
            uid = person.get("id")
            first_name = person.get("attributes", {}).get("first_name")
            last_name = person.get("attributes", {}).get("last_name")
            role = person.get("attributes", {}).get("role")
            print(f"\t - {first_name} {last_name} [{role}] ({uid})")
            if role == "team_member":
                yield uid, {"data": {"role": role, "id": uid, "type": "people"}}

    def __call__(self, interval: timedelta = None) -> Dict:
        team_members = {}
        session_to_update = set()
        sessions = self.client.sessions(self.event_id)
        for session in sessions:
            session_id = session.get("id")
            est_started_at = session.get("attributes", {}).get("estimated_started_at")
            timezone = session.get("attributes", {}).get("timezone")
            status = session.get("attributes", {}).get("status")
            if status == "upcoming" and not session_to_update:
                session_to_update.add(session_id)
            est_started_at_converted = datetime.fromtimestamp(est_started_at)
            print(
                f"# [{status.upper()}] {est_started_at_converted} {timezone} ({session_id}) "
            )
            for uid, tm in self.extract_team_members(session_id):
                team_members[uid] = tm

        verb = "re-creating" if session_to_update else "creating"

        interval = interval if interval else timedelta(days=7)
        estimated_started_at = est_started_at_converted
        while estimated_started_at < datetime.now():
            estimated_started_at += interval

        print(f"{verb} session with {len(team_members)} team members")
        print(f"planned on {estimated_started_at}")

        if session_to_update:
            for session in session_to_update:
                self.client.delete_session(session)

        new_session = self.client.create_session(
            list(team_members.values()), estimated_started_at, timezone
        )
        event_room_link = f"https://app.livestorm.co/p/{self.event_id}/live"
        session_room_link = new_session.get("attributes", {}).get("room_link")

        print(f"event room link {event_room_link}")
        print(f"room link for the newly created session: {session_room_link}")

        return new_session
