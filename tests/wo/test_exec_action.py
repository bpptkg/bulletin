import logging
import logging.config
import os
import unittest
from unittest.mock import patch

from dateutil.parser import parse
from obspy import read
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Bulletin

from wo import settings
from wo.actions import WebObsAction

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)


class ExecActionTest(unittest.TestCase):

    @patch("wo.ops.restore_event")
    @patch("wo.ops.delete_event")
    @patch("wo.ops.hide_event")
    @patch("wo.ops.mysql_upsert")
    @patch("wo.clients.webobs.WebObsMC3Fetcher")
    @patch("wo.clients.waveform.get_waveforms")
    def test_exec_action(
        self,
        mock_get_waveforms,
        mock_mc3_fetcher,
        mock_mysql_upsert,
        mock_hide_event,
        mock_delete_event,
        mock_restore_event,
    ):
        st = read(os.path.join(DATA_DIR, "stream.msd"))
        mock_get_waveforms.return_value = st

        fetcher = mock_mc3_fetcher.return_value
        with open(os.path.join(DATA_DIR, "MC3_dump_bulletin1.csv"), "rb") as fd:
            fetcher.request_mc3.return_value = fd.read()

        mock_mysql_upsert.return_value = True
        mock_hide_event.return_value = True
        mock_delete_event.return_value = True
        mock_restore_event.return_value = True

        engine = create_engine(settings.DATABASE_ENGINE)
        eventdate = parse("2021-07-08T00:02:00.240000+00:00")

        # Lazy import patched methods.
        from wo.visitor import _execute_action

        _execute_action(
            engine, Bulletin, WebObsAction.WEBOBS_UPDATE_EVENT, eventdate=eventdate
        )

        _execute_action(
            engine, Bulletin, WebObsAction.WEBOBS_HIDE_EVENT, eventid="2021-07#2380"
        )

        _execute_action(
            engine,
            Bulletin,
            WebObsAction.WEBOBS_RESTORE_EVENT,
            eventid="2021-07#2380",
            eventtype="ROCKFALL",
        )

        _execute_action(
            engine, Bulletin, WebObsAction.WEBOBS_DELETE_EVENT, eventid="2021-07#2381"
        )

        with self.assertRaises(ValueError):
            _execute_action(
                engine, Bulletin, WebObsAction.WEBOBS_HIDE_EVENT, eventid=None
            )

        with self.assertRaises(ValueError):
            _execute_action(
                engine,
                Bulletin,
                WebObsAction.WEBOBS_RESTORE_EVENT,
                eventid=None,
                eventtype="ROCKFALL",
            )

        with self.assertRaises(ValueError):
            _execute_action(
                engine,
                Bulletin,
                WebObsAction.WEBOBS_RESTORE_EVENT,
                eventid="2021-07#2380",
                eventtype=None,
            )

        with self.assertRaises(ValueError):
            _execute_action(
                engine, Bulletin, WebObsAction.WEBOBS_DELETE_EVENT, eventid=None
            )


if __name__ == "__main__":
    logging.config.dictConfig(settings.LOGGING)

    unittest.main()
