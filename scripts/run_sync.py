import argparse
import logging
import logging.config

from bulletin import settings
from bulletin.clients import webobs
from bulletin.singleton import SingleInstanceException
from bulletin.utils.date import to_datetime
from bulletin.visitor import SimpleEventVisitor
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Run WebObs to seismic bulletin database '
        'synchronization.')

    parser.add_argument(
        'start',
        help="Start time of time window in 'YYYY-mm-dd' "
        "or 'YYYY-mm-dd HH:MM:SS' format (Asia/Jakarta time zone).")

    parser.add_argument(
        'end',
        help="End time of time window in 'YYYY-mm-dd' "
        "or 'YYYY-mm-dd HH:MM:SS' format (Asia/Jakarta time zone).")

    parser.add_argument(
        '-d', '--dry',
        action='store_true',
        help='Do not insert the results to database (dry run).')

    parser.add_argument(
        '-m', '--skip-mag-calc',
        action='store_true',
        help='Skip event magnitude calculation.')

    parser.add_argument(
        '-s', '--print-only',
        action='store_true',
        help='Print events that have not been synched yet.')

    return parser.parse_args()


def main():
    logging.config.dictConfig(settings.LOGGING)

    args = parse_args()
    engine = create_engine(settings.DATABASE_ENGINE)
    Base.prepare(engine, reflect=True)

    start = to_datetime(args.start)
    end = to_datetime(args.end)

    try:
        events = webobs.fetch_mc3(start, end)

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
