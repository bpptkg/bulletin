import datetime
import logging
import time

import pandas as pd
from webobsclient import MC3Client
from webobsclient.parser import MC3Parser

from .. import constants
from ..settings import WEBOBS_HOST, WEBOBS_PASSWORD, WEBOBS_USERNAME

logger = logging.getLogger(__name__)


class FetcherError(Exception):
    pass


class WebObsMC3Fetcher:
    """
    WebObs MC3 bulletin fetcher.
    """

    def __init__(self, client=None, parser=None, max_retries=5,
                 retry_delay=10):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if client is not None:
            self.client = client
        else:
            self.client = MC3Client(
                username=WEBOBS_USERNAME, password=WEBOBS_PASSWORD)
            if WEBOBS_HOST:
                self.client.api.host = WEBOBS_HOST

        if parser is not None:
            self.parser = parser
        else:
            self.parser = MC3Parser()

    def request_mc3(self, start, end, eventtype='ALL'):
        """
        Request MC3 bulletin defined by start time, end time, and optional
        eventtype. If request succeed, return CSV string in bytes.

        Start time and end time must be a datetime.datetime type and in UTC time
        zone.

        If request failed, it will try until max retries reached. If all retries
        failed, return None.
        """
        logger.info('Fetching MC3 bulletin (%s)...', self.client.api.host)
        logger.info('Time range (UTC): %s to %s', start, end)

        for __ in range(self.max_retries):
            try:
                response, content = self.client.request(
                    starttime=start.strftime(constants.DATETIME_FORMAT),
                    endtime=end.strftime(constants.DATETIME_FORMAT),
                    type=eventtype,
                    slt=0,
                    amplitude='ALL',
                    ampoper='eq',
                    dump='bul',
                    duree='ALL',
                    graph='movsum',
                    hideloc=0,
                    located=0,
                    locstatus=0,
                    mc='MC3',
                )
                if response['status'] != '200':
                    raise FetcherError('The server returned non-200 response')
                break
            except Exception as e:
                logger.error(e)
                logger.info('Retrying in %ss...', self.retry_delay)
                time.sleep(self.retry_delay)
                content = None

        return content

    def get_mc3(self, eventdate, eventid=None, sc3id=None, eventtype=None):
        """
        Get event from WebObs MC3 bulletin defined by eventdate (UTC) and
        matching criteria (eventid, sc3id, or eventtype).

        The event is resolved with the following precedence: sc3id, eventid, and
        eventdate. eventdate has to be UTC time-aware datetime.datetime because
        WebObs MC3 eventdate also in UTC time zone. Beware that eventdate also
        takes account miliseconds part.

        If event not found after matching criteria, return None.
        """
        start = eventdate - datetime.timedelta(seconds=10)
        end = eventdate + datetime.timedelta(seconds=10)

        if eventtype is not None:
            content = self.request_mc3(start, end, eventtype=eventtype)
        else:
            content = self.request_mc3(start, end)

        if content is None:
            return None

        df = self.parser.to_df(content)
        if df.empty:
            return None

        if sc3id is not None:
            event = df.loc[df['seiscompid'] == sc3id]
            if not event.empty:
                return event.to_dict(orient='records')[0]

        if eventid is not None:
            event = df.loc[df['eventid'] == eventid]
            if not event.empty:
                return event.to_dict(orient='records')[0]

        event = df.loc[df['eventdate'] == eventdate]
        if not event.empty:
            return event.to_dict(orient='records')[0]
        return None

    def fetch_mc3_as_df(self, start, end, eventtype='ALL'):
        """
        Request MC3 bulletin defined by start time, end time, and optional
        eventtype returned as Pandas DataFrame.
        """
        content = self.request_mc3(start, end, eventtype=eventtype)
        if content is None:
            return pd.DataFrame()

        # Filter exact to allow only eventdate in the defined time range.
        df = self.parser.to_df(content)
        df = df.where((df['eventdate'] >= start) &
                      (df['eventdate'] < end))
        df.dropna(how='any', inplace=True, subset=['eventdate'])
        return df

    def fetch_mc3_as_dict(self, start, end, eventtype='ALL'):
        """
        Request MC3 bulletin defined by start time, end time, and optional
        eventtype returned as dictionary.
        """
        df = self.fetch_mc3_as_df(start, end, eventtype=eventtype)
        if df.empty:
            return {}
        return df.to_dict(orient='records')
