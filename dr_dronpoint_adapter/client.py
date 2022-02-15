import logging
import json
import os
import urllib.parse
import threading as th
import queue
import requests
import requests.auth

from dr_dronpoint_adapter.events_journal import EventList


logger = logging.getLogger()


def ping(addr):
    """
    Return ping status for specified IP address
    """
    return os.system('ping -c 1 -w 1 {} > /dev/null 2>&1'.format(addr)) == 0


class ConfigTransaction:
    """
    Helper class to hold configuration transaction.
    """
    URL_PREFIX = 'platforms/databaseline/'

    class Closed(Exception):
        """"""

    def __init__(self, client):
        self.__client = client
        self.is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self.__client.get_request('{}{}'.format(self.URL_PREFIX, 'opentransaction'))
        self.is_open = True

    def close(self):
        self.__client.get_request('{}{}'.format(self.URL_PREFIX, 'closetransaction'))
        self.is_open = False


class DRServerAPIClientBase:
    """
    Client API to access to DRServer
    There is basic functionality for connecting to server and send requests.
    """

    SSL_VERIFY = False
    BASE_API_PREFIX = 'dunai'

    class NoAccess(Exception):
        """Raises when no access to host"""

    class NoAuth(Exception):
        """Raises if authentication failed"""

    def __init__(self, host, port, username, password, schema='https'):
        self.__schema = schema
        self.__host = host
        self.__port = int(port)

        if not ping(self.__host):
            raise DRServerAPIClientBase.NoAccess

        self.__session = requests.Session()
        self.__session.auth = requests.auth.HTTPBasicAuth(username, password)
        self.__base_url = '{}://{}:{}/{}/'.format(
            self.__schema,
            self.__host,
            self.__port,
            self.BASE_API_PREFIX)

        self.__check_auth()
        self.config_transaction = ConfigTransaction(client=self)

    def __check_auth(self):
        """Checks auth credentials"""
        response = self.request('/', 'GET')
        if response.status_code == 401:
            self.close()
            raise DRServerAPIClientBase.NoAuth

    def __check_config_transaction(self):
        """Check ConfigTransaction is ready"""
        if not self.config_transaction.is_open:
            raise ConfigTransaction.Closed

    def request(self, url, method, **kwargs):
        """Send request to specified url with method"""
        url = urllib.parse.urljoin(self.__base_url, url)
        with self.__session as session:  # to sure connection will be closed
            response = session.request(
                url=url,
                method=method,
                verify=self.SSL_VERIFY,
                **kwargs)

        response.encoding = 'utf-8'

        logger.debug('\n\n{}\nRequest [{}]: {}, {}\nResponse [{}]\n{}\n\n'.format(
            '#' * 50,
            method,
            url,
            kwargs,
            response.status_code,
            '#' * 50,
        ))

        if 500 <= response.status_code < 600:
            response.raise_for_status()

        return response

    def close(self):
        self.__session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'DR Server API Client at {}:{}'.format(
            self.__host,
            self.__port)


class DRServerEventsSubscriber(th.Thread, DRServerAPIClientBase):
    """
    Thread for receiving continues stream of events from DR server.
    Connects to server, continuously receives events stream, parse stream and send it to queue.
    """

    URL_PREFIX = 'events/stream/subscribe'

    # todo: use max_size for queue (and maybe other settings)

    def __init__(self, host, port, username, password, schema='https'):
        DRServerAPIClientBase.__init__(self, host, port, username, password, schema)
        th.Thread.__init__(self)

        # flag for breaking receiving loop
        self._stop_flag = th.Event()
        # queue for received events
        self._queue = queue.Queue()

    @property
    def event_queue(self) -> queue.Queue:
        """Queue for events."""
        return self._queue

    def stop(self) -> None:
        """Command for stopping the thread."""
        self._stop_flag.set()

    def _event_handler(self, event: EventList) -> None:
        """Method for events handling - put to queue"""
        self._queue.put(event)

    def run(self) -> None:
        """
        Loop of receiving continues stream of events and parsing of it.
        """

        logger.info(f'{self.__class__.__name__}: start')

        # make request with stream flag for continues reading
        response = self.request(self.URL_PREFIX, 'GET', stream=True)

        logger.info(f'{self.__class__.__name__}: response for event subscribe: status = {response.status_code}')

        # now we can receive continues data of events
        # data is a continues string with such format: {"events":[......]}{"events":[......]}...
        # for parsing this string split it to lines by delimiter '}{'

        # create lines iterator and drop first line (it could be wrong)
        iterator = response.iter_lines(decode_unicode=True, delimiter='}{')
        iterator.__next__()

        try:
            for line in iterator:

                # check for stop flag
                if self._stop_flag.is_set():
                    logger.info(f'{self.__class__.__name__}: stop event - terminate')
                    break

                # sometimes receive zero events
                if len(line) == 0:
                    continue

                # convert json to EventList (add brackets for right json format)
                try:
                    events = EventList.from_json('{' + line + '}')

                except json.JSONDecodeError as e:
                    logger.warning(f'{self.__class__.__name__}: json decode error: {e}')
                    logger.warning(f'{self.__class__.__name__}: {line}')
                    continue

                # handle received events
                for event in events:
                    self._event_handler(event)

        except requests.exceptions.ChunkedEncodingError as e:
            logger.critical(f'{self.__class__.__name__}: server closed connection: {e}')

        finally:
            logger.info(f'{self.__class__.__name__}: finish')

            # send empty message for unblocking queue
            self._queue.put('')
