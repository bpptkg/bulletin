import logging

import pandas as pd
from webobsclient.contrib.bpptkg.db.sessions import session_scope
from .settings import TIMEZONE

logger = logging.getLogger(__name__)


def hide_event(engine, table, eventid, operator):
    with session_scope(engine) as session:
        queryset = session.query(table).get(eventid)
        if queryset is not None:
            queryset.eventtype = None
            queryset.operator = operator
            session.commit()
            return True
        return False


def restore_event(engine, table, eventid, eventtype, operator):
    with session_scope(engine) as session:
        queryset = session.query(table).get(eventid)
        if queryset is not None:
            queryset.eventtype = eventtype
            queryset.operator = operator
            session.commit()
            return True
        return False


def delete_event(engine, table, eventid, operator):
    """
    For current version, we only implement soft delete instead of actually
    delete an event in the database to prevent accidental deletion.

    Setting eventtype to None is sufficient to resemble event deletion.
    """
    with session_scope(engine) as session:
        queryset = session.query(table).get(eventid)
        if queryset is not None:
            queryset.eventtype = None
            queryset.operator = operator
            session.commit()
            return True
        return False


def mysql_upsert(engine, data):
    """
    Insert new event to database model or update the event if primary key
    exists.

    :param engine: SQLAlchemy engine, e.g. an instance created by
    create_engine() function.

    :param data: Event data, can be a dictionary or a list of dictionary. Note
    that event date must be in the UTC time zone. This function will do
    conversion to local time zone automatically.

    :returns: True if upsert succeed, otherwise return False.
    """
    insert_query = r"""
        INSERT INTO bulletin (
            eventid,
            eventdate,
            eventdate_microsecond,
            number,
            duration,
            amplitude,
            magnitude,
            longitude,
            latitude,
            depth,
            type,
            file,
            valid,
            projection,
            operator,
            timestamp,
            timestamp_microsecond,
            deles,
            labuhan,
            pasarbubar,
            pusunglondon,
            ml_deles,
            ml_labuhan,
            ml_pasarbubar,
            ml_pusunglondon,
	        locmode,
            loctype
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE
            eventdate=VALUES(eventdate),
            eventdate_microsecond=VALUES(eventdate_microsecond),
            number=VALUES(number),
            duration=VALUES(duration),
            amplitude=VALUES(amplitude),
            magnitude=VALUES(magnitude),
            longitude=VALUES(longitude),
            latitude=VALUES(latitude),
            depth=VALUES(depth),
            type=VALUES(type),
            file=VALUES(file),
            valid=VALUES(valid),
            projection=VALUES(projection),
            operator=VALUES(operator),
            timestamp=VALUES(timestamp),
            timestamp_microsecond=VALUES(timestamp_microsecond),
            deles=VALUES(deles),
            labuhan=VALUES(labuhan),
            pasarbubar=VALUES(pasarbubar),
            pusunglondon=VALUES(pusunglondon),
            ml_deles=VALUES(ml_deles),
            ml_labuhan=VALUES(ml_labuhan),
            ml_pasarbubar=VALUES(ml_pasarbubar),
            ml_pusunglondon=VALUES(ml_pusunglondon),
            locmode=VALUES(locmode),
	        loctype=VALUES(loctype)
    """
    column_names = [
        'eventid',
        'eventdate',
        'eventdate_microsecond',
        'number',
        'duration',
        'amplitude',
        'magnitude',
        'longitude',
        'latitude',
        'depth',
        'eventtype',
        'seiscompid',
        'valid',
        'projection',
        'operator',
        'timestamp',
        'timestamp_microsecond',
        'count_deles',
        'count_labuhan',
        'count_pasarbubar',
        'count_pusunglondon',
        'ml_deles',
        'ml_labuhan',
        'ml_pasarbubar',
        'ml_pusunglondon',
        'location_mode',
        'location_type',
    ]

    logger.info('Preparing event data entry.')
    if isinstance(data, dict):
        df = pd.DataFrame([data, ])
    else:
        df = pd.DataFrame(data)

    # Convert any timestamp column to local time zone.
    df['eventdate'] = df['eventdate'].dt.tz_convert(
        TIMEZONE).dt.tz_localize(None)
    df['timestamp'] = df['timestamp'].dt.tz_convert(
        TIMEZONE).dt.tz_localize(None)

    datetime_format = '%Y-%m-%d %H:%M:%S'
    df['eventdate'] = df['eventdate'].dt.strftime(datetime_format)
    df['timestamp'] = df['timestamp'].dt.strftime(datetime_format)

    df = df.astype(object).where((pd.notnull(df)), None)

    logger.info('Event entries: %s', df.to_dict(orient='records'))

    entries = map(tuple, df[column_names].values.tolist())
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        cursor.executemany(insert_query, entries)
        connection.commit()
        return True
    except Exception as e:
        logger.error(e)
        connection.rollback()
        return False
    finally:
        if connection:
            connection.close()
