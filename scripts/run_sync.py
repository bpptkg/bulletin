import argparse
import datetime
import logging
import logging.config
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if True:
    from wo import settings
    from wo.clients import webobs
    from wo.singleton import SingleInstanceException
    from wo.utils import date
    from wo.visitor import SimpleEventVisitor

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run WebObs to seismic bulletin database '
        'synchronization.')

    parser.add_argument(
        '-s', '--start',
        help="Start time of time window in 'YYYY-mm-dd' "
        "or 'YYYY-mm-dd HH:MM:SS' format (Asia/Jakarta time zone).")

    parser.add_argument(
        '-e', '--end',
        help="End time of time window in 'YYYY-mm-dd' "
        "or 'YYYY-mm-dd HH:MM:SS' format (Asia/Jakarta time zone).")

    parser.add_argument(
        '-i', '--eventtype',
        default='ALL',
        help='Run only for certain event type, e.g VTA, VTB, MP.')

    parser.add_argument(
        '-d', '--dry',
        action='store_true',
        help='Do not insert the results to database (dry run).')

    parser.add_argument(
        '-m', '--skip-mag-calc',
        action='store_true',
        help='Skip event magnitude calculation.')

    parser.add_argument(
        '-p', '--print-only',
        action='store_true',
        help='Print events that have not been synched yet.')

    return parser.parse_args()


def main():
    logging.config.dictConfig(settings.LOGGING)

    args = parse_args()
    engine = create_engine(settings.DATABASE_ENGINE, poolclass=NullPool)
    Base.prepare(engine, reflect=True)

    if args.start is not None and args.end is not None:
        start = date.to_datetime(args.start, aware=True)
        end = date.to_datetime(args.end, aware=True)
    else:
        end = date.now(aware=True)
        start = end - datetime.timedelta(days=settings.DAY_RANGE)

    starttime = date.to_utc(start)
    endtime = date.to_utc(end)
    logger.info('Time range [local]: %s to %s', start, end)
    logger.info('Time range [utc]: %s to %s', starttime, endtime)

    try:
        fetcher = webobs.WebObsMC3Fetcher()
        events = fetcher.fetch_mc3_as_dict(
            starttime, endtime, eventtype=args.eventtype)
        logger.info('Number of events: %s', len(events))

        visitor = SimpleEventVisitor(
            engine,
            Bulletin,
            lockfile=settings.LOCKFILE,
            dry=args.dry,
            skip_mag_calc=args.skip_mag_calc,
        )

        if args.print_only:
            visitor.print_events(events)
        else:
            visitor.process_events(events)

    except SingleInstanceException as e:
        logger.error(e)


if __name__ == '__main__':
    main()
