"""Integration tests for setup/unload of an color config entry."""

from __future__ import annotations

import pytest
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.color.const import (
    CONF_INITIAL_COLOR,
    CONF_INITIAL_MODE,
    DOMAIN,
    MODE_CHROMATIC,
)


@pytest.mark.asyncio
async def test_setup_and_unload_chromatic_entry(hass: HomeAssistant) -> None:
    """A chromatic config entry produces a single color.* entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Couch Color",
        data={
            CONF_NAME: "Couch Color",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FF8000",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Find the created entity. Entity IDs are auto-generated.
    states = [s for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")]
    assert len(states) == 1
    state = states[0]
    assert state.state.startswith("#")
    assert state.attributes["kind"] == "chromatic"
    assert "rgb_color" in state.attributes
    assert "xy_color" in state.attributes

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    # On unload HA keeps the entity in the registry but marks it unavailable;
    # we just verify the entry transitioned out of LOADED.
    assert entry.state.value == "not_loaded"
