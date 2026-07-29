"""Scene reproduce_state tests."""

from __future__ import annotations

import pytest
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.color.const import (
    CONF_INITIAL_COLOR,
    CONF_INITIAL_MODE,
    DOMAIN,
    MODE_CHROMATIC,
)
from custom_components.color.reproduce_state import async_reproduce_states


async def _setup_entity(hass: HomeAssistant) -> str:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="X",
        data={
            CONF_NAME: "X",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FFFFFF",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return next(
        s.entity_id for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")
    )


@pytest.mark.asyncio
async def test_reproduce_chromatic_hex(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    snapshot = State(
        entity_id,
        "#00FF00",
        {"kind": "chromatic", "brightness": None},
    )
    await async_reproduce_states(hass, [snapshot])
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    r, g, b = state.attributes["rgb_color"]
    assert g > 200
    assert state.attributes["brightness"] is None


@pytest.mark.asyncio
async def test_reproduce_white_with_brightness(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    snapshot = State(
        entity_id,
        "#FFFFFF",
        {"kind": "white", "color_temp_kelvin": 3500, "brightness": 200},
    )
    await async_reproduce_states(hass, [snapshot])
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state.attributes["kind"] == "white"
    assert state.attributes["color_temp_kelvin"] == 3500
    assert state.attributes["brightness"] == 200
