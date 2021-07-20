from django.core.management.base import BaseCommand
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from webobsclient.contrib.bpptkg.db.seismic_bulletin import Base
from wo import settings

settings.MIGRATED = False


class Command(BaseCommand):
    help = (
        'Creates seismic_bulletin schema. Use this for TESTING only.'
    )

    def handle(self, *args, **options):
        engine = create_engine(settings.DATABASE_ENGINE)
        dbname = engine.url.database

        if not database_exists(engine.url):
            self.stdout.write('Creating schema: {}'.format(dbname))
            create_database(engine.url)
            Base.prepare(engine)
            Base.metadata.create_all(engine)

            self.stdout.write(self.style.SUCCESS(
                'Created schema: {}'.format(dbname)))
        else:
            self.stdout.write(self.style.WARNING(
                'Database already exists: {}'.format(dbname)))
            Base.prepare(engine)
            Base.metadata.create_all(engine)

            self.stdout.write(self.style.SUCCESS(
                'Migrated schema: {}'.format(dbname)
            ))

        self.stdout.flush()
