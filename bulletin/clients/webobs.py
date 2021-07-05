from webobsclient import MC3Client
from webobsclient.parser import MC3Parser

from .. import constants
from ..settings import WEBOBS_HOST, WEBOBS_PASSWORD, WEBOBS_USERNAME


def fetch_mc3(starttime, endtime, eventtype='ALL'):
    """
    Fetch WebObs MC3 bulletin by particular time range and eventtype, and then
    return as dictionary.

    Note that starttime and endtime are using local time zone and be converted
    to UTC automatically.

    If error occurred during request, it will return empty list.
    """

    client = MC3Client(
        username=WEBOBS_USERNAME,
        password=WEBOBS_PASSWORD,
    )

    if WEBOBS_HOST:
        client.api.host = WEBOBS_HOST

    try:
        start = date.to_utc(date.localize(starttime))
    except ValueError:
        start = date.to_utc(starttime)

    try:
        end = date.to_utc(date.localize(endtime))
    except ValueError:
        end = date.to_utc(endtime)

    response, content = client.request(
        starttime=start.strftime(constants.DATETIME_FORMAT),
        endtime=end.strftime(constants.DATETIME_FORMAT),
        slt=0,
        type=eventtype,
        duree='ALL',
        ampoper='eq',
        amplitude='ALL',
        locstatus=0,
        located=0,
        hideloc=0,
        mc='MC3',
        dump='bul',
        graph='movsum',
    )

    if response['status'] != '200':
        return []

    parser = MC3Parser(content, use_local_tz=True)

    return parser.to_dictionary()
