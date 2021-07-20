import os
import unittest
import warnings

from decouple import config
from obspy import read
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db import query
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin
from webobsclient.parser import MC3Parser

from wo.magnitude import compute_magnitude_all
from wo.ops import mysql_upsert

DATA_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'data')


class UpsertEventsTest(unittest.TestCase):
    """
    Verify that the data inserted to database were correct, particularly for UTC
    to local time zone datetime conversion.
    """

    def test_upsert_events(self):
        # Run this test only on CI/CD environment to prevent data overwrite in
        # the seismic bulletin database.
        cicd = config('CICD', default=False, cast=bool)
        if not cicd:
            warnings.warn('You are running test_upsert_events() '
                          'not in the CI/CD environment. This will cause '
                          'accidental effect to the seismic bulletin '
                          'database. Make sure you set CICD=True in your '
                          'testing environment settings. Particularly in the '
                          'tox.ini setenv settings.')
            return

        engine_url = config('SEISMIC_BULLETIN_ENGINE')
        engine = create_engine(engine_url)
        Base.prepare(engine, reflect=True)

        with open(os.path.join(DATA_DIR,
                               'MC3_dump_bulletin1.csv'), 'rb') as fd:
            content = fd.read()

        stream = read(os.path.join(DATA_DIR, 'stream.msd'))
        magnitudes = compute_magnitude_all(stream)

        datetime_format = '%Y-%m-%d %H:%M:%S'
        parser = MC3Parser()
        events = parser.to_dict(content)

        for index in range(len(events)):
            events[index].update(magnitudes)

        ok = mysql_upsert(engine, events)
        self.assertTrue(ok)

        # Event ID: 2021-07#2380
        event_2021_07_2380 = query.get_bulletin_by_id(
            engine, Bulletin, '2021-07#2380')

        self.assertIsNotNone(event_2021_07_2380)
        self.assertEqual(event_2021_07_2380['eventid'], '2021-07#2380')
        self.assertEqual(
            event_2021_07_2380['eventdate'].strftime(datetime_format),
            '2021-07-08 07:02:00')
        self.assertEqual(event_2021_07_2380['eventdate_microsecond'], 24)

        # EventID: 2021-07#2392
        event_2021_07_2392 = query.get_bulletin_by_id(
            engine, Bulletin, '2021-07#2392')

        self.assertIsNotNone(event_2021_07_2392)
        self.assertEqual(event_2021_07_2392['eventid'], '2021-07#2392')
        self.assertEqual(
            event_2021_07_2392['eventdate'].strftime(datetime_format),
            '2021-07-08 07:09:43')
        self.assertEqual(event_2021_07_2392['eventdate_microsecond'], 60)

        # EventID: 2021-07#2382
        event_2021_07_2382 = query.get_bulletin_by_id(
            engine, Bulletin, '2021-07#2382')

        self.assertIsNotNone(event_2021_07_2382)
        self.assertEqual(event_2021_07_2382['eventid'], '2021-07#2382')
        self.assertEqual(
            event_2021_07_2382['eventdate'].strftime(datetime_format),
            '2021-07-08 07:10:11')
        self.assertEqual(event_2021_07_2382['eventdate_microsecond'], 88)


if __name__ == '__main__':
    unittest.main()
