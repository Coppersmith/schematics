
import unittest
import datetime

from schematics.types import (
    BaseType, StringType, DateTimeType, DateType, IntType, EmailType, LongType,
    URLType, GeoPointType
)
from schematics.types.temporal import MillisecondType
from schematics.exceptions import ValidationError, StopValidation, ConversionError


class TestType(unittest.TestCase):



    def test_date(self):
        today = datetime.date(2013, 3, 1)

        date_type = DateType()
        self.assertEqual(date_type("2013-03-01"), today)

        self.assertEqual(date_type.to_primitive(today), "2013-03-01")

    def test_datetime(self):
        dt = datetime.datetime.now()
        self.assertEqual(DateTimeType()(dt.isoformat()), dt)

    def test_datetime_format(self):
        dt_input = '2013.03.07 15:31'
        dt = datetime.datetime(2013, 3, 7, 15, 31)
        self.assertEqual(DateTimeType(formats=['%Y.%m.%d %H:%M'])(dt_input), dt)

    def test_datetime_primitive(self):
        output = '2013.03.07 15:31'
        dt = datetime.datetime(2013, 3, 7, 15, 31)
        dt_type = DateTimeType(serialized_format='%Y.%m.%d %H:%M')
        self.assertEqual(dt_type(dt.isoformat()), dt)
        self.assertEqual(dt_type.to_primitive(dt), output)

    def test_datetime_accepts_datetime(self):
        output = '2013.03.07 15:31'
        dt = datetime.datetime(2013, 3, 7, 15, 31)
        dt_type = DateTimeType(serialized_format='%Y.%m.%d %H:%M')
        self.assertEqual(dt_type(dt), dt)
        self.assertEqual(dt_type.to_primitive(dt), output)
        
    def test_int(self):
        with self.assertRaises(ConversionError):
            IntType()('a')
        self.assertEqual(IntType()(1), 1)

    def test_none_passed_to_geopointtype(self):
        geo_type = GeoPointType()
        self.assertEqual(geo_type(None),None)

    def test_none_passed_to_urltype(self):
        url_type = URLType()
        self.assertEqual(url_type(None),None)        

    def test_millisecond_accepts_datetime(self):
        from dateutil.parser import parse
        from time import mktime
        a_time = '2013-03-01 15:59:59'

        a_long = long(mktime(parse(a_time).timetuple())) * 1000

        millisecond_type = MillisecondType()
        
        self.assertEqual(millisecond_type(a_time), a_long)
        
    def test_millisecond(self):
        def datestring_to_millis(ds):
            """Takes a string representing the date and converts it to milliseconds
            since epoch.
            """
            from dateutil.parser import parse
            dt = parse(ds)
            return datetime_to_millis(dt)
        
        def datetime_to_millis(dt):
            """Takes a datetime instances and converts it to milliseconds since epoch.
            """
            seconds = dt.timetuple()
            from time import mktime
            seconds_from_epoch = mktime(seconds)
            return seconds_from_epoch * 1000 # milliseconds
        
        a_time = '2013-03-01 15:59:59'
        #datetime.datetime(2013, 3, 1,15,59,59)
        #print a_time
        #print long(datestring_to_millis(a_time))
        millisecond_type = MillisecondType()
        #print '**',millisecond_type(long(datestring_to_millis(a_time))),'**'
        self.assertEqual(millisecond_type(a_time),datestring_to_millis(a_time))
        
        
class TestTypeValidators(unittest.TestCase):
    def test_custom_validation_functions(self):
        class UppercaseType(BaseType):
            def validate_uppercase(self, value):
                if value.upper() != value:
                    raise ValidationError("Value must be uppercase!")

        field = UppercaseType()

        with self.assertRaises(ValidationError):
            field.validate("lowercase")

    def test_custom_validation_function_and_inheritance(self):
        class UppercaseType(StringType):

            def validate_uppercase(self, value):
                if value.upper() != value:
                    raise ValidationError("Value must be uppercase!")

        class MUppercaseType(UppercaseType):

            def __init__(self, number_of_m_chars, **kwargs):
                self.number_of_m_chars = number_of_m_chars

                super(MUppercaseType, self).__init__(**kwargs)

            def validate_contains_m_chars(self, value):
                if value.count("M") != self.number_of_m_chars:
                    raise ValidationError("Value must contain {} 'm' characters".format(self.number_of_m_chars))

        field = MUppercaseType(number_of_m_chars=3)

        field.validate("MMM")

        with self.assertRaises(ValidationError):
            field.validate("mmm")

        with self.assertRaises(ValidationError):
            field.validate("MM")


class TestEmailType(unittest.TestCase):
    def test_email_type_with_invalid_email(self):
        with self.assertRaises(ValidationError):
            EmailType().validate(u'sdfg\U0001f636\U0001f46e')


class TestURLType(unittest.TestCase):
    def test_url_type_with_invalid_url(self):
        with self.assertRaises(ValidationError):
            URLType().validate(u'http:example.com')


class TestLongType(unittest.TestCase):

    def test_raises_error(self):
        field = LongType(required=True)
        with self.assertRaises(ConversionError):
            field.convert(None)


class TestStringType(unittest.TestCase):
    def test_string_type_required(self):
        field = StringType(required=True)
        with self.assertRaises(ValidationError):
            field.validate(None)

    def test_string_type_accepts_none(self):
        field = StringType()
        field.validate(None)

    def test_string_required_accepts_empty_string(self):
        field = StringType(required=True)
        field.validate('')

    def test_string_min_length_doesnt_accept_empty_string(self):
        field = StringType(min_length=1)
        with self.assertRaises(ValidationError):
            field.validate('')

    def test_string_regex(self):
        StringType(regex='\d+').validate("1")

        with self.assertRaises(ValidationError):
            StringType(regex='\d+').validate("a")


