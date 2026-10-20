"""Serve the bundled dashboard card and load it on every dashboard.

The card lives in this package (not a separate HACS plugin) so installing the
integration is enough to get it. Its source is in the repo's `frontend/`.
"""

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

CARD_FILENAME = "input-color-card.js"
CARD_PATH = Path(__file__).parent / "www" / CARD_FILENAME
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"


async def async_register_card(hass: HomeAssistant) -> None:
    """Expose the card at CARD_URL and add it to the frontend's module list.

    An extra module URL (rather than a Lovelace resource) works for YAML-mode
    dashboards too and leaves nothing behind in storage if the integration is
    removed. The version query busts browser caches on upgrade.
    """
    # Both are after_dependencies: absent in headless test setups.
    if "frontend" not in hass.config.components or hass.http is None:
        return
    integration = await async_get_integration(hass, DOMAIN)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_PATH), cache_headers=True)]
    )
    add_extra_js_url(hass, f"{CARD_URL}?v={integration.version}")
