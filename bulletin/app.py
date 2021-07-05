import logging

from webobsclient.contrib.bpptkg.db import query

from .singleton import SingleInstance

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

            logger.info(
                'Found event: %s',
                '(ID: {}, type[webobs]: {}, type[db]: {})'.format(
                    event['eventid'],
                    event['eventtype'],
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

            logger.info('Found event ID: %s', eventid)

            event['eventdate_microsecond'] = event['eventdate'].microsecond
            event['timestamp_microsecond'] = event['timestamp'].microsecond

            if not self.skip_mag_calc:
                onset_local = date.localize(event['eventdate'])
                start = UTCDatetime(date.utc(onset_local))
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
