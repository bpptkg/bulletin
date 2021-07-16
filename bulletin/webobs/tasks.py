import time

from bulletin.celery import app
from celery.decorators import task
from django.conf import settings
from wo import visitor

from . import models


@app.task(
    bind=True,
    name='webobs_update_event',
    max_retries=5)
def update_event(self, eventdate, **kwargs):
    # For new event, WebObs may still generate eventid and synchronize the event
    # with SeisComP. So, we need to wait several seconds until the process
    # finished.
    time.sleep(settings.WEBOBS_FETCH_TIME_WAIT)

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
    visitor.delete_event(
        models.engine,
        models.Bulletin,
        eventid,
        **kwargs,
    )
