import datetime
import unittest
from pathlib import Path

from celery.utils.log import get_task_logger
from django.utils import timezone

from bulletin.webobs import schema
from wo import settings as wo_settings
from wo import visitor
from wo.clients.webobs import WebObsMC3Fetcher

logger = get_task_logger(__name__)


class TestWaveViewSync(unittest.TestCase):
    def test_sync(self) -> None:
        """
        Sync seismic bulletin database with WebObs MC3 bulletin.
        """
        fetcher = WebObsMC3Fetcher()
        csv = Path(__file__).parent / "MC3_dump_bulletin_light.csv"
        with open(csv, "rb") as fd:
            content = fd.read()
        events = fetcher.parse_mc3(content).to_dict(orient="records")

        now = timezone.now()
        start = datetime.datetime(
            now.year, now.month, now.day, tzinfo=now.tzinfo
        ) - datetime.timedelta(days=1)

        wo_settings.GET_WAVEFORMS_FUNCTION = schema.mock_get_waveforms

        if events:
            # Sync WebObs MC3 bulletin to seismic bulletin database (forward sync).
            visitor.sync_webobs_and_bulletin(
                schema.engine,
                schema.Bulletin,
                events,
            )

            # Sync seismic bulletin database to WebObs MC3 bulletin (reverse sync).
            visitor.sync_bulletin_and_webobs(
                schema.engine,
                schema.Bulletin,
                events,
                start,
                now,
            )


if __name__ == "__main__":
    unittest.main()
