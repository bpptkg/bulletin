import logging

import pandas as pd
from obspy import UTCDateTime
from webobsclient.contrib.bpptkg.db import query

from . import ops, settings
from .actions import WebObsAction
from .clients import webobs
from .clients.waveform import get_waveforms
from .magnitude import compute_magnitude_all
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
        for event, result in query.filter_exact(
                self.engine, self.table, events):
            logger.info('Event from WebObs: %s', event)

            eventid = event['eventid']
            eventtype = event['eventtype']
            eventdate = event['eventdate'].to_pydatetime()

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
                start = UTCDateTime(eventdate)
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
                ok = ops.mysql_upsert(self.engine, event)
                if ok:
                    logger.info('Event data successfully updated.')
                else:
                    logger.error('Event value failed to be updated.')


def _execute_action(
        engine,
        table,
        action,
        *,
        dry_run=False,
        eventdate=None,
        eventid=None,
        eventtype=None,
        operator=None,
        sc3id=None,
):
    """
    Process event depending on the action type.
    """

    logger.info('Triggered action: %s', action)
    logger.info('Event meta data: [eventdate: %s, eventid: %s, '
                'sc3id: %s, eventtype: %s, operator: %s]',
                eventdate, eventid, sc3id, eventtype, operator)

    if action == WebObsAction.WEBOBS_UPDATE_EVENT:
        fetcher_class = settings.WEBOBS_MC3_FETCHER_CLASS
        if fetcher_class is not None:
            fetcher = fetcher_class()
        else:
            fetcher = webobs.WebObsMC3Fetcher()
        event = fetcher.get_mc3(eventdate, eventid=eventid, sc3id=sc3id,
                                eventtype=eventtype)

        # If event is None, the calculation could not be proceeded. So, just
        # exit the function.
        if event is None:
            logger.error('Event could not be found.')
            return
        logger.info('Matched event from WebObs MC3: %s', event)

        # Calculate magnitude info.
        start = UTCDateTime(event['eventdate'])
        if event['duration'] is None or pd.isna(event['duration']):
            duration = 30.0
        else:
            duration = float(event['duration'])

        end = start + duration

        get_waveforms_func = settings.GET_WAVEFORMS_FUNCTION
        if get_waveforms_func is not None:
            if not callable(get_waveforms_func):
                raise ValueError(
                    'GET_WAVEFORMS_FUNCTION value must be a function '
                    'instead of type of {}'.format(type(get_waveforms_func)))
            stream = get_waveforms_func(start, end)
        else:
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
        if eventid is None:
            raise ValueError('Action %s requires eventid value not None',
                             WebObsAction.WEBOBS_HIDE_EVENT)

        if dry_run:
            logger.info('Using dry run. Event is not hidden.')
        else:
            ok = ops.hide_event(engine, table, eventid, operator)
            if ok:
                logger.info('Event successfully hidden.')
            else:
                logger.error('Event failed to be hidden.')

    elif action == WebObsAction.WEBOBS_RESTORE_EVENT:
        if eventid is None:
            raise ValueError('Action %s requires eventid value not None',
                             WebObsAction.WEBOBS_RESTORE_EVENT)

        if eventtype is None:
            raise ValueError('Action %s requires eventtype value not None',
                             WebObsAction.WEBOBS_RESTORE_EVENT)

        if dry_run:
            logger.info('Using dry run. Event is not restored.')
        else:
            ok = ops.restore_event(engine, table, eventid, eventtype, operator)
            if ok:
                logger.info('Event successfully restored.')
            else:
                logger.error('Event failed to be restore.')

    elif action == WebObsAction.WEBOBS_DELETE_EVENT:
        if eventid is None:
            raise ValueError('Action %s requires eventid value not None',
                             WebObsAction.WEBOBS_DELETE_EVENT)

        if dry_run:
            logger.info('Using dry run. Event is not deleted.')
        else:
            ok = ops.delete_event(engine, table, eventid, operator)
            if ok:
                logger.info('Event successfully deleted.')
            else:
                logger.error('Event failed to be deleted.')

    else:
        logger.error('Unsupported action: %s', action)


def update_event(
        engine,
        table,
        eventdate,
        *,
        eventid=None,
        sc3id=None,
        eventtype=None,
        operator=None,
):
    """
    Update an event in the database.

    Update can be creating a new event or updating existing event.
    """
    _execute_action(
        engine, table, WebObsAction.WEBOBS_UPDATE_EVENT,
        eventdate=eventdate,
        eventid=eventid,
        sc3id=sc3id,
        eventtype=eventtype,
        operator=operator,
    )


def hide_event(engine, table, eventid, **kwargs):
    """
    Hide an event in the database.
    """
    _execute_action(
        engine,
        table,
        WebObsAction.WEBOBS_HIDE_EVENT,
        eventid=eventid,
        **kwargs,
    )


def restore_event(engine, table, eventid, eventtype, **kwargs):
    """
    Restore an event in the database.
    """
    _execute_action(
        engine,
        table,
        WebObsAction.WEBOBS_RESTORE_EVENT,
        eventid=eventid,
        eventtype=eventtype,
        **kwargs,
    )


def delete_event(engine, table, eventid, **kwargs):
    """
    Delete an event in the database.
    """
    _execute_action(
        engine,
        table,
        WebObsAction.WEBOBS_DELETE_EVENT,
        eventid=eventid,
        **kwargs,
    )
