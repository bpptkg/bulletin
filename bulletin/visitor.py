import logging

from obspy import UTCDateTime
from webobsclient.contrib.bpptkg.db import query

from .clients.waveform import get_waveforms
from .magnitude import compute_magnitude_all
from .ops import mysql_upsert
from .singleton import SingleInstance
from .utils import date

logger = logging.getLogger(__name__)


class SimpleEventVisitor(SingleInstance):

    def __init__(self, engine, table, *, lockfile='', flavor_id='',
                 dry=False, skip_mag_calc=False):
        self.engine = engine
        self.table = table
        self.dry = dry
        self.skip_mag_calc = skip_mag_calc

        super().__init__(flavor_id=flavor_id, lockfile=lockfile)

    def print_events(self, events):
        """
        Print all events that have been not synched between WebObs and database.
        """
        for event, result in query.filter_exact(
            self.engine,
            self.table,
            events,
        ):
            if result is None:
                eventtype_db = None
            else:
                eventtype_db = result['eventtype']

            eventid = event['eventid']
            eventtype = event['eventtype']
            eventdate = event['eventdate']

            logger.info(
                'Found event: %s',
                '(ID: {}, eventdate[local]: {}, type[webobs]: {}, '
                'type[db]: {})'.format(
                    eventid,
                    eventdate,
                    eventtype,
                    eventtype_db,
                )
            )

    def filter_events(self, events):
        """
        Filter any event that has not been synched between WebObs and database.
        """
        results = []
        for event, result in query.filter_exact(
            self.engine,
            self.table,
            events,
        ):
            results.append(event)

        return results

    def process_events(self, events):
        """
        Process all events that have not been synched between WebObs and
        database.
        """
        for event, result in query.filter_exact(self.engine, self.table, events):
            eventid = event['eventid']
            eventtype = event['eventtype']
            eventdate = event['eventdate']

            if result is None:
                eventtype_db = None
            else:
                eventtype_db = result['eventtype']

            logger.info(
                'Found event: %s',
                '(ID: {}, eventdate[local]: {}, type[webobs]: {}, '
                'type[db]: {})'.format(
                    eventid,
                    eventdate,
                    eventtype,
                    eventtype_db,
                )
            )

            if not self.skip_mag_calc:
                try:
                    onset_local = date.localize(
                        date.to_datetime(event['eventdate']))
                except ValueError as e:
                    onset_local = date.to_datetime(event['eventdate'])

                start = UTCDateTime(date.to_utc(onset_local))
                try:
                    duration = float(event['duration'])
                except Exception:
                    duration = 30

                end = start + duration

                logger.info('Event ID: %s', eventid)
                logger.info('Event type: %s', eventtype)
                logger.info('Event date (UTC): %s', start)
                logger.info('Event date (Local): %s', onset_local)
                logger.info('Fetch time window (UTC): %s to %s', start, end)

                stream = get_waveforms(start, end)
                if stream is not None:
                    logger.info('Stream:')
                    logger.info(stream.__str__(extended=True))

                magnitudes = compute_magnitude_all(stream)
                logger.info('Magnitude info: %s', magnitudes)
                event.update(magnitudes)

            logger.info('Event data: %s', event)

            if not event:
                logger.warning('Event data is empty. Skipping.')
                continue

            if self.dry:
                logger.info('Using dry run. Results not inserted to database.')
            else:
                ok = mysql_upsert(self.engine, event)
                if ok:
                    logger.info('Event data successfully updated.')
                else:
                    logger.error('Event value failed to be updated.')
