import logging

import pandas as pd
from obspy import UTCDateTime
from webobsclient.contrib.bpptkg.db import query

from . import dbquery, ops, settings
from .actions import WebObsAction
from .clients import webobs
from .clients.waveform import get_waveforms
from .magnitude import compute_magnitude_all
from .singleton import SingleInstance

logger = logging.getLogger(__name__)


def reverse_process_event_and_updatedb(engine, table, event_db, event_wo, *,
                                       dry_run=False):
    """
    Reverse process event by synchronizing event in the bulletin database to the
    WebBbs MC3 bulletin. If dry_run is True, don't update the database.

    If event_wo is None, it means that event exists in the database but not in
    the MC3. So, we need to hide this event.

    If event_wo exists in the database but has different eventtype, restore the
    event.
    """
    eventid = event_db['eventid']
    operator = event_db['operator']

    if event_wo is None:
        if dry_run:
            logger.info('Using dry run. Event is not hidden.')
        else:
            ok = ops.hide_event(engine, table, eventid, operator)
            if ok:
                logger.info('Event successfully hidden.')
            else:
                logger.error('Event failed to be hidden.')

    else:
        eventtype_wo = event_wo['eventtype']
        operator_wo = event_wo['operator']

        if dry_run:
            logger.info('Using dry run. Event is not restored.')
        else:
            ok = ops.restore_event(
                engine, table, eventid, eventtype_wo, operator_wo)
            if ok:
                logger.info('Event successfully restored.')
            else:
                logger.error('Event failed to be restore.')


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

        :param events: List of dictionary of WebObs events.
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
                '(ID: {}, eventdate[local]: {}, type[wo]: {}, '
                'type[db]: {})'.format(
                    eventid,
                    eventdate,
                    eventtype,
                    eventtype_db,
                )
            )

    def reverse_print_events(self, events, start, end, eventtype=None):
        """
        Print all events in the database that are not in the WebObs MC3
        bulletin.

        :param events: List of dictionary of WebObs events.

        :param start: Start time to query database in UTC time zone.

        :param end: End time to query database in UTC time zone.

        :param eventtype: Event type, e.g. VTA, VTB.
        """
        for event, wo_event in dbquery.reverse_filter_exact(
            self.engine,
            self.table,
            events,
            start,
            end,
            eventtype,
        ):
            if wo_event is None:
                eventtype_wo = None
            else:
                eventtype_wo = wo_event['eventtype']

            logger.info(
                'Found event: %s',
                '(ID: {}, eventdate[local]: {}, type[db]: {}, '
                'type[wo]: {})'.format(
                    event['eventid'],
                    event['eventdate'],
                    event['eventtype'],
                    eventtype_wo,
                )
            )

    def reverse_process_events(self, events, start, end, eventtype=None):
        """
        Process all events in the database that are not in the WebObs MC3
        bulletin.

        :param events: List of dictionary of WebObs events.

        :param start: Start time to query database in UTC time zone.

        :param end: End time to query database in UTC time zone.

        :param eventtype: Event type, e.g. VTA, VTB.
        """
        for event, wo_event in dbquery.reverse_filter_exact(
            self.engine,
            self.table,
            events,
            start,
            end,
            eventtype,
        ):
            if wo_event is None:
                eventtype_wo = None
            else:
                eventtype_wo = wo_event['eventtype']

            logger.info(
                'Found event: %s',
                '(ID: {}, eventdate[local]: {}, type[db]: {}, '
                'type[wo]: {})'.format(
                    event['eventid'],
                    event['eventdate'],
                    event['eventtype'],
                    eventtype_wo,
                )
            )

            reverse_process_event_and_updatedb(
                self.engine,
                self.table,
                event,
                wo_event)

    def filter_events(self, events):
        """
        Filter any event that has not been synched between WebObs and database.

        :param events: List of dictionary of WebObs events.
        """
        results = []
        for event, _ in query.filter_exact(
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

        :param events: List of dictionary of WebObs events.
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
                '(ID: {}, eventdate[local]: {}, type[wo]: {}, '
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
            else:
                stream = None

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


def process_event_and_updatedb(engine, event, *, dry_run=False):
    """
    Process event by calculating necessary fields and update to database. If
    dry_run is True, don't update the database.
    """

    # Calculate magnitude info.
    start = UTCDateTime(event['eventdate'])
    if event['duration'] is None or pd.isna(event['duration']):
        # Set default duration to 30 seconds.
        duration = 30.0
    else:
        duration = float(event['duration'])

    end = start + duration

    get_waveforms_func = settings.GET_WAVEFORMS_FUNCTION
    if get_waveforms_func is not None:
        if not callable(get_waveforms_func):
            raise ValueError(
                'GET_WAVEFORMS_FUNCTION must be a callable function '
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


def sync_webobs_and_bulletin(engine, table, events, *, dry_run=False):
    """
    Synchronize events between webobs and bulletin database. If any of the event
    not exists or has different eventtype, process the event and update the
    database.
    """
    for event_wo, event_db in query.filter_exact(engine, table, events):
        if event_db is None:
            eventtype_db = None
        else:
            eventtype_db = event_db['eventtype']

        logger.info(
            'Found event: ('
            'eventid: {}, '
            'eventdate[utc]: {}, '
            'type[wo]: {}, '
            'type[db]: {})'.format(
                event_wo['eventid'],
                event_wo['eventdate'],
                event_wo['eventtype'],
                eventtype_db)
        )

        process_event_and_updatedb(engine, event_wo, dry_run=dry_run)


def sync_bulletin_and_webobs(engine, table, events, start, end, *,
                             eventtype=None, dry_run=False):
    """
    Synchronize events between bulletin database and WebBbs. If any of the event
    not exists or has different eventtype, process the event and update the
    database.
    """
    for event_db, event_wo in dbquery.reverse_filter_exact(
        engine,
        table,
        events,
        start,
        end,
        eventtype=eventtype,
    ):
        if event_wo is None:
            eventtype_wo = None
        else:
            eventtype_wo = event_wo['eventtype']

        logger.info(
            'Found event: ('
            'eventid: {}, '
            'eventdate[local]: {}, '
            'type[db]: {}, '
            'type[wo]: {})'.format(
                event_db['eventid'],
                event_db['eventdate'],
                event_db['eventtype'],
                eventtype_wo)
        )

        reverse_process_event_and_updatedb(
            engine, table, event_db, event_wo, dry_run=dry_run)


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

        process_event_and_updatedb(engine, event, dry_run=dry_run)

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
