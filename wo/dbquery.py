import logging

import pandas as pd
import pytz
from webobsclient.contrib.bpptkg.db.sessions import session_scope
from webobsclient.contrib.bpptkg.utils.sqlalchemy import object_as_dict

from .settings import TIMEZONE

logger = logging.getLogger(__name__)


def get_bulletin_by_range(engine, table, starttime, endtime, eventtype):
    """
    Get bulletin by particular time range and eventtype.

    :param engine: SQLAlchemy engine.

    :param table: Seismic bulletin model or table.

    :param starttime: Start time of query in local time zone.

    :param endtime: End time of query in local time zone.

    :param eventtype: Event type, e.g. VTA, VTB. If eventtype is None or ALL,
    query all events (excluding None). ALL eventtype is used by WebObs to query
    all event types.
    """
    logger.info('Database eventtype query: %s', eventtype)

    with session_scope(engine) as session:
        queryset = session.query(table).filter(
            table.eventdate >= starttime,
            table.eventdate < endtime,
        )
        if eventtype == 'ALL':
            queryset = queryset.filter(table.eventtype != None)
        elif isinstance(eventtype, str):
            queryset = queryset.filter(table.eventtype == eventtype)
        elif isinstance(eventtype, (list, tuple)):
            queryset = queryset.filter(table.eventtype.in_(eventtype))
        else:
            queryset = queryset.filter(table.eventtype != None)

        logger.debug('Queryset: %s', queryset)

        results = queryset.order_by(table.eventdate).all()
        return [object_as_dict(item) for item in results]


def reverse_filter_exact(engine, table, wo_events, start, end, eventtype=None):
    """
    Generator function to check if particular event not exists (event ID not
    exists, or event ID exists but eventtype differ) in the webobs.

    :param engine: SQLAlchemy engine.

    :param table: Bulletin model or table.

    :param wo_events: List of dictionary of events fetched from WebObs MC3
    bulletin.

    :param start: Start time to query database in UTC time zone.

    :param end: End time to query database in UTC time zone.

    :param eventtype: Event type, e.g. VTA, VTB.

    :return: Yield a tuple of database event and WebObs event (None if not
    matched), e.g. (event_db, event_wo). event_db is a dictionary of event in
    the database while event_wo is a dictionary of event in the WebObs. Note
    that eventdate in the database always uses local time zone while eventdate
    in the WebObs uses UTC time zone.
    """

    df = pd.DataFrame(wo_events)

    if not df.empty:
        localtz = pytz.timezone(TIMEZONE)
        starttime = start.astimezone(localtz).replace(tzinfo=None)
        endtime = end.astimezone(localtz).replace(tzinfo=None)

        logger.info('Database query time range (local): %s to %s',
                    starttime, endtime)

        logger.info('Fetching bulletin data from database...')
        db_events = get_bulletin_by_range(
            engine, table, starttime, endtime, eventtype)

        logger.info('Fetched %s events from database.', len(db_events))

        eventids = set(df['eventid'])
        for event in db_events:
            eventid = event['eventid']
            if eventid not in eventids:
                yield (event, None)
            else:
                matched_event = df.loc[
                    df['eventid'] == eventid
                ].to_dict(orient='records')[0]
                if matched_event['eventtype'] != event['eventtype']:
                    yield (event, matched_event)
