import logging

from webobsclient.contrib.bpptkg.db import query
from .singleton import SingleInstance

logger = logging.getLogger(__name__)


class SimpleApp(SingleInstance):

    def __init__(self, engine, table, *, lockfile='', flavor_id=''):
        self.engine = engine
        self.table = table

        super().__init__(flavor_id=flavor_id, lockfile=lockfile)

    def process_events(self, events):
        for event in query.filter_not_exists(self.engine, self.table, events):
            logger.info('Found event ID: %s', event['eventid'])
