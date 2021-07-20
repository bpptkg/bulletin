import os
import unittest

from dateutil.parser import parse
from webobsclient import MC3Client

from wo.clients.webobs import WebObsMC3Fetcher

DATA_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'data')


class CustomWebObsMC3Fetcher(WebObsMC3Fetcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request_mc3(self, start, end, eventtype='ALL'):
        with open(os.path.join(DATA_DIR, 'MC3_dump_bulletin1.csv'),
                  'rb') as fd:
            return fd.read()


class WebObsMC3FetcherTest(unittest.TestCase):

    def setUp(self):
        client = MC3Client(username='test', password='test')
        self.fetcher = CustomWebObsMC3Fetcher(client=client)

    def test_query_event_by_eventdate(self):

        eventdate = parse('2021-07-08T00:02:00.240000+00:00')
        event = self.fetcher.get_mc3(eventdate)

        self.assertIsNotNone(event)
        self.assertEqual(event['eventid'], '2021-07#2380')
        self.assertEqual(event['eventtype'], 'ROCKFALL')

    def test_query_event_by_eventid(self):
        eventdate = parse('2021-07-08T00:04:19.000+00:00')

        event = self.fetcher.get_mc3(eventdate, eventid='2021-07#2381')

        self.assertIsNotNone(event)
        self.assertEqual(event['eventid'], '2021-07#2381')
        self.assertEqual(event['eventtype'], 'ROCKFALL')

    def test_query_event_by_sc3id(self):
        eventdate = parse('2021-07-08T00:10:11.880000+00:00')

        event = self.fetcher.get_mc3(eventdate, sc3id='://bpptkg2021nhcvwk')

        self.assertIsNotNone(event)
        self.assertEqual(event['eventid'], '2021-07#2382')
        self.assertEqual(event['eventtype'], 'ROCKFALL')


if __name__ == '__main__':
    unittest.main()
