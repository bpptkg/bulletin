from bulletin import settings
from bulletin.app import SimpleApp
from sqlalchemy import create_engine
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base, Bulletin
import logging
import logging.config


def main():
    logging.config.dictConfig(settings.LOGGING)
    
    engine = create_engine(settings.DATABASE_ENGINE)
    table = Bulletin

    Base.prepare(engine, reflect=True)

    events = [
        {'eventid': '2021-03#2145'},
        {'eventid': '2021-03#2142'},
        {'eventid': '2021-03#2141'},
        {'eventid': '2021-03#2146'},
        {'eventid': '2021-03#2147'},
    ]

    app = SimpleApp(engine, table)
    app.process_events(events)


if __name__ == '__main__':
    main()
