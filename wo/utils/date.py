import datetime

import pytz
from dateutil.parser import parse

from ..settings import TIMEZONE


def localize(d, timezone=TIMEZONE):
    if d.tzinfo is not None:
        raise ValueError('Date value is already has timezone info set.')
    return pytz.timezone(timezone).localize(d)


def to_utc(d):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        return d.astimezone(pytz.utc)
    return pytz.utc.localize(d)


def to_local(d, timezone=TIMEZONE):
    if d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None:
        return d.astimezone(pytz.timezone(timezone))
    return pytz.timezone(timezone).localize(d)


def to_datetime(d, aware=False):
    date_obj = parse(d)

    if aware:
        if date_obj.tzinfo is None:
            return localize(date_obj)
        return date_obj
    return date_obj


def now(aware=False):
    if aware:
        return datetime.datetime.now(pytz.timezone(TIMEZONE))
    return datetime.datetime.now()
