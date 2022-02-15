import json


class EventList:
    """ Model for events journal record"""

    class Category:
        """Events category"""
        IDLE = 0
        WARNING = 1
        ALARM = 2

    def __init__(self,
                 event_id,
                 info_row_id,
                 event_class,
                 start_time,
                 update_time,
                 end_time,
                 category,
                 action,
                 latitude,
                 longitude,
                 distance,
                 piquet,
                 comment,
                 current_speed
                 ):
        """
        Initialization of sensor events journal record
        :param event_id: Identifier of sensor event
        :param info_row_id: ???
        :param event_class: Identifier of event class
        :param start_time: Start time of event (format: Unix time)
        :param update_time: Time of last update for event (format: Unix time)
        :param end_time: End time of event if event is finished (format: Unix time)
        :param category: Event category (Idle, Warning, Alarm)
        :param action: Event handling action
        :param latitude, longitude: Event coordinates
        :param distance: Information about sensor point, list of dictionaries (platform_id, distance)
        :param piquet: Information about piquets, list of dictionaries (platform_id, object_id, piquet_id)
        :param comment: Additional info
        :param current_speed: Current speed
        """
        self.__event_id = event_id
        self.__info_row_id = info_row_id
        self.__event_class = event_class
        self.__start_time = start_time
        self.__update_time = update_time
        self.__end_time = end_time
        self.__category = category
        self.__action = action
        self.__latitude = latitude
        self.__longitude = longitude
        self.__distance = distance
        self.__piquet = piquet
        self.__comment = comment
        self.__current_speed = current_speed

    def __str__(self):
        return '{}'.format(self.as_dict())

    def __repr__(self):
        return self.__str__()

    @property
    def pk(self):
        return self.__event_id

    @property
    def event_id(self):
        return self.__event_id

    @property
    def info_row_id(self):
        return self.__info_row_id

    @info_row_id.setter
    def info_row_id(self, info_row_id):
        self.__info_row_id = info_row_id

    @property
    def event_class(self):
        return self.__event_class

    @event_class.setter
    def event_class(self, event_class):
        self.__event_class = event_class

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def update_time(self):
        return self.__update_time

    @update_time.setter
    def update_time(self, update_time):
        self.__update_time = update_time

    @property
    def end_time(self):
        return self.__end_time

    @end_time.setter
    def end_time(self, end_time):
        self.__end_time = end_time

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, category):
        self.__category = category

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.__action = action

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, latitude):
        self.__latitude = latitude

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, longitude):
        self.__longitude = longitude

    @property
    def distance(self):
        return self.__distance

    @distance.setter
    def distance(self, distance):
        self.__distance = distance

    @property
    def piquet(self):
        return self.__piquet

    @piquet.setter
    def piquet(self, piquet):
        self.__piquet = piquet

    @property
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, comment):
        self.__comment = comment

    @property
    def current_speed(self):
        return self.__current_speed

    @current_speed.setter
    def current_speed(self, current_speed):
        self.__current_speed = current_speed

    def as_dict(self):
        return {
            "id": self.__event_id,
            "info_row_id": self.__info_row_id,
            "event_class": self.__event_class,
            "start_time": self.__start_time,
            "update_time": self.__update_time,
            "end_time": self.__end_time,
            "category": self.__category,
            "action": self.__action,
            "latitude": self.__latitude,
            "longitude": self.__longitude,
            "distance": self.__distance,
            "piquet": self.__piquet,
            "comment": self.__comment,
            "current_speed": self.__current_speed
        }

    @classmethod
    def from_json(cls, text):
        """Return list of events by json response text."""
        res = []
        for e_dict in json.loads(text).get('events', []):
            res.append(cls(
                event_id=e_dict.get('id'),
                info_row_id=e_dict.get('info_row_id'),
                event_class=e_dict.get('event_class'),
                start_time=e_dict.get('start_time'),
                update_time=e_dict.get('update_time'),
                end_time=e_dict.get('end_time'),
                category=e_dict.get('category'),
                action=e_dict.get('action'),
                latitude=e_dict.get('latitude'),
                longitude=e_dict.get('longitude'),
                distance=e_dict.get('distance'),
                piquet=e_dict.get('piquet'),
                comment=e_dict.get('comment'),
                current_speed=e_dict.get('current_speed')
            ))
        return res
