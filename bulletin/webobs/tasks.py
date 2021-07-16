import time

from celery.decorators import task
from django.conf import settings
from wo import visitor

from . import models


@task(name='webobs_update_event')
def update_event(eventdate, **kwargs):
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


@task(name='webobs_hide_event')
def hide_event(eventid, **kwargs):
    visitor.hide_event(
        models.engine,
        models.Bulletin,
        eventid,
        **kwargs,
    )


@task(name='webobs_restore_event')
def restore_event(eventid, eventtype, **kwargs):
    visitor.restore_event(
        models.engine,
        models.Bulletin,
        eventid,
        eventtype,
        **kwargs,
    )


@task(name='webobs_delete_event')
def delete_event(eventid, **kwargs):
    visitor.delete_event(
        models.engine,
        models.Bulletin,
        eventid,
        **kwargs,
    )
