import time

from bulletin.celery import app
from celery.decorators import task
from celery.utils.log import get_task_logger
from django.conf import settings
from wo import visitor

from . import models

logger = get_task_logger(__name__)


@app.task(
    bind=True,
    name='webobs_update_event',
    max_retries=5)
def update_event(self, eventdate, **kwargs):
    """
    Update an event in the database.
    """

    # For a new event, WebObs may still generate eventid and synchronize the
    # event with SeisComP. So, we need to wait several seconds until the process
    # finished.
    logger.info('Waiting for {}s before executing task...'.format(
        settings.WEBOBS_UPDATE_EVENT_DELAY))
    time.sleep(settings.WEBOBS_UPDATE_EVENT_DELAY)

    visitor.update_event(
        models.engine,
        models.Bulletin,
        eventdate,
        **kwargs,
    )


@app.task(
    bind=True,
    name='webobs_hide_event',
    max_retries=5)
def hide_event(self, eventid, **kwargs):
    """
    Hide an event in the database.
    """
    visitor.hide_event(
        models.engine,
        models.Bulletin,
        eventid,
        **kwargs,
    )


@app.task(
    bind=True,
    name='webobs_restore_event',
    max_retries=5)
def restore_event(self, eventid, eventtype, **kwargs):
    """
    Restore an event in the database.
    """
    visitor.restore_event(
        models.engine,
        models.Bulletin,
        eventid,
        eventtype,
        **kwargs,
    )


@app.task(
    bind=True,
    name='webobs_delete_event',
    max_retries=5)
def delete_event(self, eventid, **kwargs):
    """
    Delete an event in the database, i.e. soft delete.
    """
    visitor.delete_event(
        models.engine,
        models.Bulletin,
        eventid,
        **kwargs,
    )
