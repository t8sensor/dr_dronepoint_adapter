import logging
import urllib3

from dr_dronpoint_adapter import \
    DronPointAlarmAdapter, \
    DronPointNotificator, \
    DRServerEventsSubscriber


urllib3.disable_warnings()


logging.basicConfig(level=logging.INFO)
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


def main():
    """
    Example of using DronPointAlarmAdapter.
    """

    # create subscriber to server events
    subscriber = DRServerEventsSubscriber(
        host='127.0.0.1',
        port=5082,
        schema='https',
        username='xxxxx',
        password='xxxxx')

    # create notificator for test server
    notificator = DronPointNotificator(
        host='127.0.0.1',
        port=50411)

    # create adapter for notify about alarm objects
    adapter = DronPointAlarmAdapter(
        target_classes_id=[TARGET_CLASSES_SERVER_IDS['human__step']],
        subscriber=subscriber,
        notificator=notificator
    )

    # run adapter (could be stopped by keyboard interrupt)
    adapter.run()


if __name__ == '__main__':
    main()
