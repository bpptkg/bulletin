from urllib.parse import quote, urljoin

import requests

from .config import conf
from .serializers import sanitize


class WaveViewClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.api = requests.Session()
        self.api.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )

    def update(self, event: dict) -> None:
        url = urljoin(
            conf.base_url,
            f"/api/v1/organizations/{conf.organization_id}/volcanoes/{conf.volcano_id}/catalogs/{conf.catalog_id}/bma-bulletin/{quote(event['eventid'])}/",
        )
        payload = sanitize(event)
        if not payload:
            return
        response = self.api.put(url, json=payload)
        response.raise_for_status()

    def delete(self, event_id: str) -> None:
        url = urljoin(
            conf.base_url,
            f"/api/v1/organizations/{conf.organization_id}/volcanoes/{conf.volcano_id}/catalogs/{conf.catalog_id}/bma-bulletin/{quote(event_id)}/",
        )
        response = self.api.delete(url)
        response.raise_for_status()
