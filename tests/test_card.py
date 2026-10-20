"""Tests for serving the bundled dashboard card."""

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.color.card import CARD_PATH, CARD_URL
from custom_components.color.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


def test_bundled_card_is_packaged() -> None:
    """The built card ships inside the integration package."""
    assert CARD_PATH.is_file()
    assert "input-color-card" in CARD_PATH.read_text()


async def test_card_registered_when_frontend_loaded(hass: HomeAssistant) -> None:
    """With the frontend up, the card is served and added as a module."""
    hass.config.components.add("frontend")
    hass.http = MagicMock(async_register_static_paths=AsyncMock())
    with patch("custom_components.color.card.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})

    (paths,) = hass.http.async_register_static_paths.call_args.args
    assert [(p.url_path, p.path) for p in paths] == [(CARD_URL, str(CARD_PATH))]
    add_js.assert_called_once()
    assert add_js.call_args.args[1].startswith(f"{CARD_URL}?v=")


async def test_card_skipped_without_frontend(hass: HomeAssistant) -> None:
    """Headless setups (no frontend) still set up cleanly."""
    with patch("custom_components.color.card.add_extra_js_url") as add_js:
        assert await async_setup_component(hass, DOMAIN, {})
    add_js.assert_not_called()
