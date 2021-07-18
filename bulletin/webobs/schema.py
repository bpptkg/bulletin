import os

from django.conf import settings
from obspy import read
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin
from wo import settings as wo_settings
from wo.clients.webobs import WebObsMC3Fetcher

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

MINISEED_DIR = os.path.join(THIS_DIR, 'miniseed')

FIXTURES_DIR = os.path.join(THIS_DIR, 'fixtures')

engine = create_engine(wo_settings.DATABASE_ENGINE,
                       pool_recycle=wo_settings.CONN_MAX_AGE)

if wo_settings.MIGRATED:
    Base.prepare(engine, reflect=True)


def mock_get_waveforms(starttime, endtime):
    """
    Mock `wo.clients.waveform.get_waveforms()` function.
    """
    st = read(os.path.join(MINISEED_DIR, 'stream.msd'))
    return st


class MockWebObsMC3Fetcher(WebObsMC3Fetcher):
    """
    Mock `wo.clients.webobs.WebObsMC3Fetcher` class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request_mc3(self, start, end, eventtype='ALL'):
        with open(os.path.join(FIXTURES_DIR,
                               'MC3_dump_bulletin.csv'), 'rb') as fd:
            return fd.read()


if settings.MOCK_SEISCOMP_SERVER:
    wo_settings.GET_WAVEFORMS_FUNCTION = mock_get_waveforms

if settings.MOCK_WEBOBS_SERVER:
    wo_settings.WEBOBS_MC3_FETCHER_CLASS = MockWebObsMC3Fetcher
