import json
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "waveview.json"


@dataclass
class WaveViewConfig:
    base_url: str
    login_url: str
    refresh_url: str
    get_account_url: str
    username: str
    password: str
    organization_id: str
    volcano_id: str
    catalog_id: str
    enable_sync: bool


def read_config() -> WaveViewConfig:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("WaveView config file not found.")
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    username = data.get("username")
    if not username:
        raise ValueError("Username is required.")
    password = data.get("password")
    if not password:
        raise ValueError("Password is required.")

    base_url = data.get("base_url")
    login_url = f"{base_url}/api/v1/auth/token/"
    refresh_url = f"{base_url}/api/v1/auth/token/refresh/"
    get_account_url = f"{base_url}/api/v1/account/"

    organization_id = data.get("organization_id")
    if not organization_id:
        raise ValueError("Organization ID is required.")
    volcano_id = data.get("volcano_id")
    if not volcano_id:
        raise ValueError("Volcano ID is required.")
    catalog_id = data.get("catalog_id")
    if not catalog_id:
        raise ValueError("Catalog ID is required.")
    enable_sync = data["enable_sync"]

    return WaveViewConfig(
        base_url=base_url,
        login_url=login_url,
        refresh_url=refresh_url,
        get_account_url=get_account_url,
        username=username,
        password=password,
        organization_id=organization_id,
        volcano_id=volcano_id,
        catalog_id=catalog_id,
        enable_sync=enable_sync,
    )


conf = read_config()
