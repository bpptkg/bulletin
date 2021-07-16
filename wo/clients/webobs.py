import datetime
import logging
import time

from webobsclient import MC3Client
from webobsclient.parser import MC3Parser

from .. import constants
from ..settings import WEBOBS_HOST, WEBOBS_PASSWORD, WEBOBS_USERNAME
from ..utils import date

logger = logging.getLogger(__name__)


def fetch_mc3(start, end, eventtype='ALL'):
    """
    Fetch WebObs MC3 bulletin by particular time range and eventtype, and then
    return as dictionary.

    Note that starttime and endtime are using UTC time zone.

    If error occurred during request, it will return empty list.
    """

    client = MC3Client(username=WEBOBS_USERNAME, password=WEBOBS_PASSWORD)

    if WEBOBS_HOST:
        client.api.host = WEBOBS_HOST

    logger.info('Fetching MC3 bulletin (%s)...', client.api.host)
    logger.info('Start time (UTC): %s', start)
    logger.info('End time (UTC): %s', end)

    response, content = client.request(
        starttime=start.strftime(constants.DATETIME_FORMAT),
        endtime=end.strftime(constants.DATETIME_FORMAT),
        type=eventtype,
        amplitude='ALL',
        ampoper='eq',
        dump='bul',
        duree='ALL',
        graph='movsum',
        hideloc=0,
        located=0,
        locstatus=0,
        mc='MC3',
        slt=0,
    )

    if response['status'] != '200':
        return []

    parser = MC3Parser()
    return parser.to_dict(content)


class WebObsMC3Fetcher:

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
        logger.info('Fetching MC3 bulletin (%s)...', self.client.api.host)
        logger.info('Time range (UTC): %s to %s', start, end)

        for i in range(self.max_retries):
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
                break
            except Exception as e:
                logger.error(e)
                logger.info('Retrying in %ss...', self.retry_delay)
                time.sleep(self.retry_delay)
                content = None

        return content

    def get_mc3(self, eventdate, eventid=None, sc3id=None, eventtype=None):
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

        if eventid is not None:
            event = df.loc[df['eventid'] == eventid]
            if not event.empty:
                return event.to_dict(orient='records')[0]

        if sc3id is not None:
            event = df.loc[df['seiscompid'] == sc3id]
            if not event.empty:
                return event.to_dict(orient='records')[0]

        event = df.loc[df['eventdate'] == eventdate]
        if not event.empty:
            return event.to_dict(orient='records')[0]
        return None
