import logging

import pandas as pd
from webobsclient.bpptkg.db.sessions import session_scope

logger = logging.getLogger(__name__)


def hide_event(engine, table, eventid):
    with session_scope(engine) as session:
        queryset = session.query(table).get(eventid)
        if queryset is not None:
            queryset.eventtype = None
            session.commit()
            return True
        return False


def delete_event(engine, table, eventid):
    with session_scope(engine) as session:
        queryset = session.query(table).get(eventid)
        if queryset is not None:
            queryset.delete()
            session.commit()
            return True
        return False


def mysql_upsert(engine, data):
    """
    Insert new data to database model or update the value if primary key exists.
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

    df = pd.DataFrame([data, ])
    df = df.where((pd.notnull(df)), None)

    data = map(tuple, df[column_names].values.tolist())
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        cursor.executemany(insert_query, data)
        connection.commit()
        return True
    except Exception as e:
        logger.error(e)
        connection.rollback()
        return False
    finally:
        if connection:
            connection.close()
