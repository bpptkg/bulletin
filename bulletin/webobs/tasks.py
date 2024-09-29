import datetime
import time

from bulletin.celery import app
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone
from wo import visitor
from wo.clients.webobs import WebObsMC3Fetcher

from . import schema

logger = get_task_logger(__name__)


@app.task(bind=True, name="webobs_update_event", max_retries=5)
def update_event(self, eventdate, **kwargs):
    """
    Update or create an event in the database.
    """

    # For a new event, WebObs may still generate eventid and synchronize the
    # event with SeisComP. So, we need to wait several seconds until the process
    # finished.
    logger.info(
        "Waiting for {}s before executing task...".format(
            settings.WEBOBS_UPDATE_EVENT_DELAY
        )
    )
    time.sleep(settings.WEBOBS_UPDATE_EVENT_DELAY)

    visitor.update_event(
        schema.engine,
        schema.Bulletin,
        eventdate,
        **kwargs,
    )


@app.task(bind=True, name="webobs_hide_event", max_retries=5)
def hide_event(self, eventid, **kwargs):
    """
    Hide an event in the database.
    """
    visitor.hide_event(
        schema.engine,
        schema.Bulletin,
        eventid,
        **kwargs,
    )


@app.task(bind=True, name="webobs_restore_event", max_retries=5)
def restore_event(self, eventid, eventtype, **kwargs):
    """
    Restore an event in the database.
    """
    visitor.restore_event(
        schema.engine,
        schema.Bulletin,
        eventid,
        eventtype,
        **kwargs,
    )


@app.task(bind=True, name="webobs_delete_event", max_retries=5)
def delete_event(self, eventid, **kwargs):
    """
    Delete an event in the database.
    """
    visitor.delete_event(
        schema.engine,
        schema.Bulletin,
        eventid,
        **kwargs,
    )


@app.task(name="webobs_sync_events")
def sync_events(**kwargs):
    """
    Synchronize events between WebObs MC3 and seismic bulletin database and vice
    versa.

    Concurrent execution of update event signal and sync events signal may lead
    to old data replacement. To mitigate this effect, we need to increase the
    time range of WebObs MC3 fetching.
    """
    fetcher = WebObsMC3Fetcher()
    now = timezone.now()
    start = datetime.datetime(
        now.year, now.month, now.day, tzinfo=now.tzinfo
    ) - datetime.timedelta(days=1)
    events = fetcher.fetch_mc3_as_dict(start, now)
    if events:
        # Sync WebObs MC3 bulletin to seismic bulletin database (forward sync).
        visitor.sync_webobs_and_bulletin(
            schema.engine,
            schema.Bulletin,
            events,
            **kwargs,
        )

        # Sync seismic bulletin database to WebObs MC3 bulletin (reverse sync).
        visitor.sync_bulletin_and_webobs(
            schema.engine,
            schema.Bulletin,
            events,
            start,
            now,
            **kwargs,
        )


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Register periodic tasks.
    """
    sender.add_periodic_task(
        crontab(minute=0), sync_events.s(), name="sync events every 1 hour"
    )
