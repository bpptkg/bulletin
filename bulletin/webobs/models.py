import os

from django.conf import settings
from obspy import read
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin
from wo import settings as wo_settings

MINISEED_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'miniseed')

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


if settings.MOCK_SEISCOMP_SERVER:
    wo_settings.GET_WAVEFORMS_FUNCTION = mock_get_waveforms
