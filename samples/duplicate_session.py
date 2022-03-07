import logging
import sys

import isodate

from livestorm-client-py import LivestormClient
from livestorm-client-py.session_duplicator import SessionDuplicator


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    event_id = sys.argv[-3]
    token = sys.argv[-2]
    interval = isodate.parse_duration(sys.argv[-1])

    client = LivestormClient(token)
    duplicate = SessionDuplicator(client, event_id)
    duplicate(interval)
