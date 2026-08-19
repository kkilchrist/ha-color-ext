"""Tests for `color.apply_to`, the custom-integration-only dispatcher.

Core deliberately omits this action (the helper is a value; callers splat
`color_params` into `light.turn_on`). It stays in the custom integration
because 0.1.x installations already call it, so it needs its own coverage.
"""

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.color.const import (
    CONF_INITIAL_COLOR,
    CONF_INITIAL_KELVIN,
    CONF_INITIAL_MODE,
    DOMAIN,
    FIELD_BRIGHTNESS,
    FIELD_KELVIN,
    FIELD_LIGHTS,
    FIELD_OVERRIDE_BRIGHTNESS,
    MODE_CHROMATIC,
    MODE_WHITE,
    SERVICE_APPLY_TO,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_COLOR,
)
from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.core import HomeAssistant


async def _create_entry(hass: HomeAssistant, name: str = "C", **data: Any) -> str:
    """Set up an entry and return the entity_id of its color entity."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=name,
        data={
            CONF_NAME: name,
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FFFFFF",
            **data,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return next(
        s.entity_id
        for s in hass.states.async_all()
        if s.entity_id.startswith(f"{DOMAIN}.")
    )


async def _apply(hass: HomeAssistant, entity_id: str, **fields: Any) -> list:
    """Call apply_to against a mocked light.turn_on and return the calls."""
    calls = async_mock_service(hass, "light", "turn_on")
    await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_TO,
        {ATTR_ENTITY_ID: entity_id, **fields},
        blocking=True,
    )
    return calls


async def test_chromatic_sends_xy(hass: HomeAssistant) -> None:
    """A chromatic color goes out as xy_color."""
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "hex_value": "#FF8000"},
        blocking=True,
    )
    calls = await _apply(hass, entity_id, **{FIELD_LIGHTS: ["light.a"]})

    assert len(calls) == 1
    assert calls[0].data[ATTR_ENTITY_ID] == ["light.a"]
    assert "xy_color" in calls[0].data
    assert "color_temp_kelvin" not in calls[0].data
    # Brightness is left alone unless asked for.
    assert "brightness" not in calls[0].data


async def test_white_sends_kelvin(hass: HomeAssistant) -> None:
    """A white color goes out as color_temp_kelvin, not xy."""
    entity_id = await _create_entry(
        hass, **{CONF_INITIAL_MODE: MODE_WHITE, CONF_INITIAL_KELVIN: 2700}
    )
    calls = await _apply(hass, entity_id, **{FIELD_LIGHTS: ["light.a", "light.b"]})

    assert len(calls) == 1
    assert calls[0].data["color_temp_kelvin"] == 2700
    assert "xy_color" not in calls[0].data
    assert calls[0].data[ATTR_ENTITY_ID] == ["light.a", "light.b"]


async def test_override_brightness_pushes_stored_value(hass: HomeAssistant) -> None:
    """Stored brightness rides along only when override_brightness is set."""
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 120},
        blocking=True,
    )

    calls = await _apply(hass, entity_id, **{FIELD_LIGHTS: ["light.a"]})
    assert "brightness" not in calls[0].data

    calls = await _apply(
        hass, entity_id, **{FIELD_LIGHTS: ["light.a"], FIELD_OVERRIDE_BRIGHTNESS: True}
    )
    assert calls[0].data["brightness"] == 120


async def test_explicit_brightness_wins_over_stored(hass: HomeAssistant) -> None:
    """An explicit brightness beats override_brightness + stored value."""
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 200},
        blocking=True,
    )
    calls = await _apply(
        hass,
        entity_id,
        **{
            FIELD_LIGHTS: ["light.a"],
            FIELD_OVERRIDE_BRIGHTNESS: True,
            FIELD_BRIGHTNESS: 30,
        },
    )
    assert calls[0].data["brightness"] == 30


async def test_explicit_brightness_without_stored(hass: HomeAssistant) -> None:
    """An explicit brightness works with no stored brightness at all."""
    entity_id = await _create_entry(hass)
    calls = await _apply(
        hass, entity_id, **{FIELD_LIGHTS: ["light.a"], FIELD_BRIGHTNESS: 45}
    )
    assert calls[0].data["brightness"] == 45


async def test_stored_brightness_zero_is_not_none(hass: HomeAssistant) -> None:
    """brightness=0 is a real value, not 'unset' — it must survive the push."""
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 0},
        blocking=True,
    )
    calls = await _apply(
        hass, entity_id, **{FIELD_LIGHTS: ["light.a"], FIELD_OVERRIDE_BRIGHTNESS: True}
    )
    assert calls[0].data["brightness"] == 0


async def test_empty_target_is_a_noop(hass: HomeAssistant) -> None:
    """No lights means no service call, not an error."""
    entity_id = await _create_entry(hass)
    calls = await _apply(hass, entity_id, **{FIELD_LIGHTS: []})
    assert calls == []


@pytest.mark.parametrize("kelvin", [1000, 20000])
async def test_kelvin_bounds_round_trip(hass: HomeAssistant, kelvin: int) -> None:
    """Both ends of the accepted kelvin range dispatch unchanged."""
    entity_id = await _create_entry(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, FIELD_KELVIN: kelvin},
        blocking=True,
    )
    calls = await _apply(hass, entity_id, **{FIELD_LIGHTS: ["light.a"]})
    assert calls[0].data["color_temp_kelvin"] == kelvin
