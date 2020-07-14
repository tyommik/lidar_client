import json
import time
from datetime import date


class Event:
    def __init__(self, source_name, event_type, message="", timestamp=0, alarm_status=False):
        self.source = source_name
        self.event_type = event_type
        self.message = message
        self.timestamp = int(timestamp) or int(time.time())
        self.last_report = self.timestamp
        self.alarm_status = alarm_status

    def __repr__(self):
        return "{0}: {1}, {2}, {3}, {4}".format(self.source,
                                                self.event_type,
                                                self.message,
                                                self.timestamp,
                                                self.last_report
                                                )

    def __eq__(self, other):
        if self.source == other.source and self.event_type == other.event_type and self.message == other.message :
            return True
        return False

    def __hash__(self):
        return hash(str(self.source)) + hash(str(self.event_type))

    def update_last_timestamp(self, event):
        self.last_report = event.last_report

    def set_source(self, source):
        self.source = source

    def set_alarm(self):
        self.alarm_status = True

    def is_alarm(self):
        return self.alarm_status

    def to_json(self):
        dtimestamp = date.fromtimestamp(self.timestamp)
        timestamp = dtimestamp.strftime("%Y-%d-%mT%H:%M:%S") + dtimestamp.strftime(".%f")[:5]
        dump = {
            "timestamp": int(self.timestamp), # unixtime
            "source_name": self.source,
            "event_type": self.event_type,
            "description": self.message
        }
        return json.dumps(dump, ensure_ascii=False)


if __name__ == '__main__':
    event1 = Event(source_name="One",
                  event_type="111",
                  message="test_message_one",
                  timestamp=123
                  )
    event2 = Event(source_name="O1ne",
                  event_type="111",
                  message="test_message_two",
                  timestamp=123
                  )

    d = {}
    d[event1] = True
    print(event2 in d)