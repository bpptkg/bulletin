import datetime

import pandas as pd
from webobsclient.contrib.bpptkg.db import query

from .settings import TIMEZONE


def reverse_filter_exact(engine, table, wo_events):
    """
    Generator function to check if particular event not exists (event ID not
    exists, or event ID exists but eventtype differ) in the webobs.

    :param engine: SQLAlchemy engine.

    :param table: Bulletin model or table.

    :param wo_events: List of dictionary of events fetched from WebObs MC3
    bulletin.
    """

    df = pd.DataFrame(wo_events)

    if not df.empty:
        eventdatemin = df['eventdate'].min()
        eventdatemax = df['eventdate'].max()

        start = eventdatemin.dt.tz_convert(
            TIMEZONE).dt.tz_localize(None).to_pydatetime()
        end = eventdatemax.dt.tz_convert(
            TIMEZONE).dt.tz_localize(None).to_pydatetime()

        starttime = start
        # Add more seconds because endtime query is always less than the value.
        endtime = end + datetime.timedelta(seconds=2)

        db_events = query.get_bulletin_all_by_range(
            engine, table, starttime, endtime)

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
