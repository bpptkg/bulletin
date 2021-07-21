import logging

import pandas as pd
import pytz
from webobsclient.contrib.bpptkg.db.sessions import session_scope
from webobsclient.contrib.bpptkg.utils.sqlalchemy import object_as_dict

from .settings import TIMEZONE

logger = logging.getLogger(__name__)


def get_bulletin_by_range(engine, table, starttime, endtime, eventtype):
    """
    Get bulletin by particular time range and eventtype. If eventtype is None,
    query all events (excluding None).
    """
    with session_scope(engine) as session:
        queryset = session.query(table).filter(
            table.eventdate >= starttime,
            table.eventdate < endtime,
            table.eventtype != None,
        )
        if isinstance(eventtype, str):
            queryset = queryset.filter(table.eventtype == eventtype)
        elif isinstance(eventtype, (list, tuple)):
            queryset = queryset.filter(table.eventtype.in_(eventtype))
        else:
            queryset = queryset

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

        for event in db_events:
            eventid = event['eventid']
            if eventid not in df['eventid']:
                yield (event, None)
            else:
                matched_event = df.loc[
                    df['eventid'] == event['eventid']
                ].to_dict(orient='records')[0]
                if matched_event['eventtype'] != event['eventtype']:
                    yield (event, matched_event)
