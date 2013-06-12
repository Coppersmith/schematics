from __future__ import absolute_import

import datetime
from time import mktime
from dateutil.parser import parse

try:
    from dateutil.tz import tzutc, tzlocal
except ImportError:
    raise ImportError(
        'Using the datetime fields requires the dateutil library. '
        'You can obtain dateutil from http://labix.org/python-dateutil'
    )

from .base import DateTimeType, LongType


class TimeStampType(DateTimeType):
    """Variant of a datetime field that saves itself as a unix timestamp (int)
    instead of a ISO-8601 string.
    """

    def __set__(self, instance, value):
        """Will try to parse the value as a timestamp.  If that fails it
        will fallback to DateTimeType's value parsing.

        A datetime may be used (and is encouraged).
        """
        if not value:
            return

        try:
            value = TimeStampType.timestamp_to_date(value)
        except TypeError:
            pass

        super(TimeStampType, self).__set__(instance, value)

    @classmethod
    def timestamp_to_date(cls, value):
        return datetime.datetime.fromtimestamp(value, tz=tzutc())

    @classmethod
    def date_to_timestamp(cls, value):
        if value.tzinfo is None:
            value = value.replace(tzinfo=tzlocal())
        return int(round(mktime(value.astimezone(tzutc()).timetuple())))

    def to_primitive(self, value):
        v = TimeStampType.date_to_timestamp(value)
        return v

class MillisecondType(LongType):
    """For storing data as milliseconds since epoch (long) instead of one of the various
    string formats, with some helpful built-in conversions.
    """

    def __set__(self, instance, value):
        """Will try to parse the value using python's dateutil."""

        if not value:
            return

        if isinstance(value, str):
            try:
                value=MillisecondType.datestring_to_millis(value)
            except TypeError:
                pass

        super(MillisecondType, self).__set__(instance, value)

    def convert(self, value):
        if value is None:
            return None

        if not isinstance(value, (unicode,str,long,int)):
            raise ConversionError(self.messages['convert'])
        if isinstance(value, (unicode,str)): 
            value=MillisecondType.datestring_to_millis(value)
        
        return value

    
    @classmethod
    def datestring_to_millis(cls, value):
        """Takes a string representing the date and converts it to milliseconds
        since epoch.
        """
        dt = parse(value)
        return cls.datetime_to_millis(dt)

    @classmethod
    def datetime_to_millis(cls, dt):
        """Takes a datetime instances and converts it to milliseconds since epoch.
        """
        seconds = dt.timetuple()
        seconds_from_epoch = mktime(seconds)
        return seconds_from_epoch * 1000 # milliseconds

    @classmethod
    def millis_to_datetime(ms):
        """Converts milliseconds into it's datetime equivalent
        """
        seconds = ms / 1000.0
        return datetime.fromtimestamp(seconds)

