import logging

from .auth import JwtAuthentication
from .client import WaveViewClient
from .config import conf
from .retry import retry

logger = logging.getLogger(__name__)


class WaveViewAdapter:
    def __init__(self) -> None:
        self.auth = JwtAuthentication()
        self.client = WaveViewClient(self.auth.authenticate())

    @retry(max_retries=3, retry_delay=5)
    def update_event(self, event: dict) -> None:
        if not conf.enable_sync:
            return
        self.client.update(event)

    @retry(max_retries=3, retry_delay=5)
    def delete_event(self, event_id: str) -> None:
        if not conf.enable_sync:
            return
        self.client.delete(event_id)
