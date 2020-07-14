import sys

from loguru import logger

from event import Event


logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")


class NullHandler:

    def __init__(self, successor=None):
        self.__successor = successor

    def handle(self, data, eventlist, connection_info):
        if self.__successor is not None:
            self.__successor.handle(data, eventlist, connection_info)
        else:
            return eventlist


class S1ShieldAlarm(NullHandler):
    type_ = 'Downfall'
    source_name = 'S1'
    message_ = 'Срабатывание защитного поля S1'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[28][1]:
            event.set_alarm()

        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class S2ShieldAlarm(NullHandler):
    type_ = 'Downfall'
    source_name = 'S2'
    message_ = 'Срабатывание защитного поля S2'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[28][2]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class S1DirtyOnSensor(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение сканера S1'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[4][3]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class S2DirtyOnSensor(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение сканера S2'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[4][7]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class EntryDirtyOnSensor(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение сканера Entry'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[9][3]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class ExitDirtyOnSensor(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение сканера Exit'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[9][7]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class SubPlatformScannerDirtyOnSensor(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение подплатформенных сканеров'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[16][3]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class MutingOnEntry(NullHandler):
    type_ = 'TrainTrespassing'
    source_name = 'Entry'
    message_ = 'Мьютинг по сканеру Entry'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[21][0]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class MutingOnExit(NullHandler):
    type_ = 'MutingOnExit'
    source_name = 'Exit'
    message_ = 'Мьютинг по сканеру Exit'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[21][1]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class ProximitySensorDirtyOnScanner(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Загрязнение сканеров приближения поезда'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[21][3]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class SystemError(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Ошибка системы'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[22][3]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class ProtectiveShieldNormal(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Защитное поле активно, нарушений нет'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[22][0]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class MutingActiveted(NullHandler):
    type_ = 'SystemFailure'
    source_name = 'System'
    message_ = 'Мьютинг активирован'

    def handle(self, data, eventlist, connection_info):
        event = Event(source_name=connection_info["source_name"],
                      event_type=self.type_,
                      message=self.message_,
                      timestamp=connection_info["timestamp"]
                      )
        if not data[22][2]:
            event.set_alarm()
        eventlist.append(event)
        return super().handle(data, eventlist, connection_info)


class Chain:
    """
    Chain of responsibility for payload parsing

    """
    def __init__(self):

        self.chain = NullHandler()
        logger.info('Supported types: [sensor, event_type, source_name]')
        for sub_class in NullHandler.__subclasses__():
            self.chain = sub_class(self.chain)
            logger.info('{s}\t{t}\t{d}', s=sub_class.source_name, t=sub_class.type_, d=sub_class.message_)
        logger.info('---------------------------------------------------')

    def handle(self, data, eventlist, connection_info):
        self.chain.handle(data, eventlist, connection_info)
        return eventlist