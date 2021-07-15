import logging

import pandas as pd
from obspy import UTCDateTime
from webobsclient.contrib.bpptkg.db import query

from .clients.waveform import get_waveforms
from .magnitude import compute_magnitude_all
from . import ops
from .singleton import SingleInstance
from .utils import date
from .actions import WebObsAction

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
        for event, result in query.filter_exact(
                self.engine, self.table, events):
            logger.info('Event from WebObs: %s', event)

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
                if (
                    (event['duration'] is None) or
                    (pd.isna(event['duration']))
                ):
                    duration = 30.0
                else:
                    duration = float(event['duration'])

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


def process_action(engine, table, eventid, action, eventdate=None, dry_run=False):
    if action == WebObsAction.WEBOBS_UPDATE_EVENT:
        event = webobs.get_event(eventid, eventdate)
        if event is None:
            return

        # Calculate magnitude info.
        try:
            onset_local = date.localize(date.to_datetime(event['eventdate']))
        except ValueError as e:
            onset_local = date.to_datetime(event['eventdate'])
        start = UTCDateTime(date.to_utc(onset_local))
        if event['duration'] is None or pd.isna(event['duration']):
            duration = 30.0
        else:
            duration = float(event['duration'])

        end = start + duration

        stream = get_waveforms(start, end)
        if stream is not None:
            logger.info(stream.__str__(extended=True))

        magnitudes = compute_magnitude_all(stream)
        logger.info('Magnitude info: %s', magnitudes)
        event.update(magnitudes)

        # Insert to database.
        logger.info('Event data: %s', event)
        if not event:
            logger.warning('Event data is empty.')

        if dry_run:
            logger.info('Using dry run. Event is not inserted to database.')
        else:
            ok = ops.mysql_upsert(engine, event)
            if ok:
                logger.info('Event data successfully updated.')
            else:
                logger.error('Event data failed to be updated.')

    elif action == WebObsAction.WEBOBS_HIDE_EVENT:
        ok = ops.hide_event(eventid)
        if ok:
            logger.info('Event successfully hidden from database.')
        else:
            logger.error('Event failed to be hidden from database.')

    elif action == WebObsAction.WEBOBS_DELETE_EVENT:
        ok = ops.delete_event(eventid)
        if ok:
            logger.info('Event successfully deleted from database.')
        else:
            logger.error('Event failed to be deleted from database.')

    else:
        logger.error('Unsupported action: %s', action)


def update_event(engine, table, eventid):
    pass


def hide_event(eventid):
    pass


def delete_event(eventid):
    pass
