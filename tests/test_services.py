"""Service-call tests: set_color shapes, set_brightness, apply_to dispatch."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.input_color.const import (
    CONF_INITIAL_COLOR,
    CONF_INITIAL_MODE,
    DOMAIN,
    FIELD_BRIGHTNESS,
    FIELD_LIGHTS,
    FIELD_OVERRIDE_BRIGHTNESS,
    MODE_CHROMATIC,
    SERVICE_APPLY_TO,
    SERVICE_CLEAR_BRIGHTNESS,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_COLOR,
)


async def _create_entry(hass: HomeAssistant, name: str = "C") -> str:
    """Set up a chromatic entry and return its entity_id."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=name,
        data={
            CONF_NAME: name,
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FFFFFF",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    states = [s for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")]
    assert states, "entity was not created"
    return states[0].entity_id


@pytest.mark.asyncio
async def test_set_color_via_hex(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "hex_value": "#FF0000"},
        blocking=True,
    )
    state = hass.states.get(entity_id)
    assert state is not None
    # Hex round-trips through xy with some gamut loss; the red component
    # should still dominate.
    r, g, b = state.attributes["rgb_color"]
    assert r > 200
    assert g < 50
    assert b < 50


@pytest.mark.asyncio
async def test_set_color_via_kelvin_marks_white(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "color_temp_kelvin": 3000},
        blocking=True,
    )
    state = hass.states.get(entity_id)
    assert state.attributes["kind"] == "white"
    assert state.attributes["color_temp_kelvin"] == 3000


@pytest.mark.asyncio
async def test_set_color_via_color_name(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "color_name": "blue"},
        blocking=True,
    )
    state = hass.states.get(entity_id)
    r, g, b = state.attributes["rgb_color"]
    assert b > 200


@pytest.mark.asyncio
async def test_set_brightness_then_clear(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 180},
        blocking=True,
    )
    assert hass.states.get(entity_id).attributes["brightness"] == 180

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CLEAR_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    assert hass.states.get(entity_id).attributes["brightness"] is None


@pytest.mark.asyncio
async def test_apply_to_chromatic_sends_xy(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "hex_value": "#FF0000"},
        blocking=True,
    )

    captured: list[dict[str, Any]] = []

    async def _capture(call: Any) -> None:
        captured.append(dict(call.data))

    hass.services.async_register("light", "turn_on", _capture)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_TO,
        {
            ATTR_ENTITY_ID: entity_id,
            FIELD_LIGHTS: ["light.fake"],
            FIELD_OVERRIDE_BRIGHTNESS: False,
        },
        blocking=True,
    )

    assert len(captured) == 1
    data = captured[0]
    assert data["entity_id"] == ["light.fake"]
    assert "xy_color" in data
    assert "color_temp_kelvin" not in data
    # Brightness not stored => not included even without override flag work.
    assert "brightness" not in data


@pytest.mark.asyncio
async def test_apply_to_white_sends_kelvin(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "color_temp_kelvin": 2700},
        blocking=True,
    )

    captured: list[dict[str, Any]] = []

    async def _capture(call: Any) -> None:
        captured.append(dict(call.data))

    hass.services.async_register("light", "turn_on", _capture)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_TO,
        {ATTR_ENTITY_ID: entity_id, FIELD_LIGHTS: ["light.fake"]},
        blocking=True,
    )
    assert captured[0]["color_temp_kelvin"] == 2700
    assert "xy_color" not in captured[0]


@pytest.mark.asyncio
async def test_apply_to_override_brightness(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 150},
        blocking=True,
    )

    captured: list[dict[str, Any]] = []

    async def _capture(call: Any) -> None:
        captured.append(dict(call.data))

    hass.services.async_register("light", "turn_on", _capture)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_TO,
        {
            ATTR_ENTITY_ID: entity_id,
            FIELD_LIGHTS: ["light.fake"],
            FIELD_OVERRIDE_BRIGHTNESS: True,
        },
        blocking=True,
    )
    assert captured[0]["brightness"] == 150


@pytest.mark.asyncio
async def test_set_color_rejects_multiple_shapes(hass: HomeAssistant) -> None:
    entity_id = await _create_entry(hass)
    from homeassistant.exceptions import HomeAssistantError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_COLOR,
            {
                ATTR_ENTITY_ID: entity_id,
                "hex_value": "#FF0000",
                "rgb_color": [0, 255, 0],
            },
            blocking=True,
        )
