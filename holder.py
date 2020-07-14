from typing import Generic, TypeVar, Sequence, List
import time
from event import Event
from loguru import logger
import sys
from config import LOG_LEVEL

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level=LOG_LEVEL)


EventT = TypeVar('EventT')


class Holder:
    """ Держит в себе все сработки"""
    def __init__(self, event_hold_time=4):
        self.events = []
        self.event_hold_time = event_hold_time
        self.stop_list = {}

    def __contains__(self, item):
        for event in self.events:
            if event == item:
                return True
        return False

    def __index__(self, item):
        if item not in self.events:
            raise ValueError("{0} not in list".format(item))
        for idx in range(len(self.events)):
            if self.events[idx] == item:
                return idx
        assert False

    def index(self, item):
        return self.__index__(item)

    def add(self, item: EventT):
        """ Добавить сработку в список ожидания """
        if item in self.events:
            idx = self.events.index(item)
            self.events[idx].update_last_timestamp(item)
        else:
            self.events.append(item)

    def check_if_event_changed(self, source, event_type):
        tmp_event = Event(source, event_type)
        if tmp_event in self.events:
            self.events.remove(tmp_event)

    def decision_maker(self, events):
        handled_events = []
        for event in events:
            if event not in self.stop_list:
                self.stop_list[event] = False

            # if event.is_alarm() and self.stop_list[event]:
            #     continue
            # elif not event.is_alarm() and not self.stop_list[event]:
            #     continue
            if event.is_alarm() and not self.stop_list[event]:
                handled_events.append(event)
                self.stop_list[event] = True
            elif not event.is_alarm() and self.stop_list[event]:
                # TODO добавить логику для отменённых статусов
                logger.debug('Reset event: {event}', event=event)
                self.stop_list[event] = False

        return handled_events

    def get_ready_events(self):
        """ Обновляет список актуальных событий """
        current_time = int(time.time()) # int
        # candidates = [event for event in self.events if (current_time - event.timestamp > self.event_hold_time) and
        #               current_time - event.last_report < 2 * 2]
        candidates = [event for event in self.events.copy() if (current_time - event.timestamp > self.event_hold_time)]
        handled_candidates = self.decision_maker(candidates)
        logger.debug('Sending events: {events}', events=handled_candidates)
        for c in candidates:
            self.events.remove(c)
        return handled_candidates