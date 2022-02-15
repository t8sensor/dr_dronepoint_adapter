import datetime
import logging
import urllib.parse
import requests

from typing import List, Dict
from dr_dronpoint_adapter.client import DRServerEventsSubscriber, EventList


logger = logging.getLogger()


# mapping of classes name to id
TARGET_CLASSES_SERVER_IDS = {
    'human__digg': 1,
    'human__step': 2,
    'auto-car__move': 3,
    'auto-track__move': 9,
    'auto-track__digg': 10,
    'gate': 17,
    'shooting': 16,
    'animals': 11,
}


class BaseNotificator:
    """
    Base class for notify about alarms.
    """

    def alarm(self, event: EventList) -> None:
        """Notify about alarm, send event class and position"""
        raise NotImplementedError


class DronPointNotificator(BaseNotificator):
    """
    Class for notify test server about alarms.
    """

    _alarm_notify_url = '/alarm_notification/'

    def __init__(self, host: str, port: int, schema: str = 'http'):
        self._host = host
        self._port = port
        self._schema = schema

        self._base_url = f'{self._schema}://{self._host}:{self._port}/'

    def alarm(self, event: EventList) -> None:
        """Notify about alarm, send event class and position"""

        try:
            url = urllib.parse.urljoin(self._base_url, self._alarm_notify_url)
            requests.get(f'{url}?class={event.event_class}&lat={event.latitude}&lon={event.longitude}')

            logger.info(f'ALARM {event.event_class}-{event.event_id} '
                        f'{datetime.datetime.fromtimestamp(event.start_time)} {event.distance}')

        except requests.ConnectionError as e:
            logger.warning(f'{self.__class__.__name__}: {e}')


class DronPointAlarmAdapter:
    """
    Class for monitoring alarm events of target classes and notify.
    """

    def __init__(
            self,
            target_classes_id: List[int],
            subscriber: DRServerEventsSubscriber,
            notificator: BaseNotificator
    ):
        # target classes id (exception raise for wrong classes)
        self.target_classes_id = target_classes_id

        # subscribe to all events from server
        self.subscriber = subscriber

        # notificator of alarms
        self.notificator = notificator

        # dictionary of alarmed objects [object id: last event]
        self.active_objects: Dict[int, EventList] = dict()

    def run(self):
        # start subscriber in a thread
        self.subscriber.start()

        # in infinite loop handle events - stop in case of KeyboardInterrupt or subscriber finished
        try:
            while True:
                # get new event from subscriber
                event = self.subscriber.event_queue.get()

                # check subscriber is alive (if it crashed - finish)
                if not self.subscriber.is_alive():
                    break

                # drop non-targeted events
                if event.event_class not in self.target_classes_id:
                    continue

                # drop non-alarm events
                if not event.category == EventList.Category.ALARM:
                    continue

                # notify about new alarm object
                if event.event_id not in self.active_objects:
                    self.notificator.alarm(event)

                # update last event for active object
                self.active_objects[event.event_id] = event

                # check if object is finished (field end_time is not None)
                if event.end_time is not None:
                    del self.active_objects[event.event_id]

        except KeyboardInterrupt:
            logger.warning(f'Received KeyboardInterrupt - terminate ourself')

        finally:
            # stop subscriber and wait until the end
            self.subscriber.stop()
            self.subscriber.join()

            logger.info(f'Finished')
