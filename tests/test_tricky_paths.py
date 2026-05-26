"""Tests for the non-trivial behaviors flagged by the test-rigor audit.

These tests intentionally target paths where regressions would silently
corrupt user data or break promised semantics:
- Full restart round-trip via mock_restore_cache_with_extra_data
- Reproduce-state with malformed snapshot state
- Options flow + update listener actually applying icon changes
- brightness=0 distinct from brightness=None across apply_to
- Kelvin cleared when a chromatic input replaces a previously-white color
- Empty target list is a no-op (not an error)
- _coerce_color_input fallback for unexpected shapes
- _STRIP_KEYS lets through targeting keys (area_id etc.) without confusing normalize
"""

from __future__ import annotations

from typing import Any

from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME
from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache_with_extra_data,
)

from custom_components.input_color.config_flow import (
    CONF_ICON,
    _coerce_color_input,
)
from custom_components.input_color.const import (
    ATTR_KIND,
    CONF_INITIAL_BRIGHTNESS,
    CONF_INITIAL_COLOR,
    CONF_INITIAL_KELVIN,
    CONF_INITIAL_MODE,
    DEFAULT_HEX,
    DOMAIN,
    FIELD_BRIGHTNESS,
    FIELD_LIGHTS,
    FIELD_OVERRIDE_BRIGHTNESS,
    MODE_CHROMATIC,
    MODE_WHITE,
    SERVICE_APPLY_TO,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_COLOR,
    STATE_SCHEMA_VERSION,
)
from custom_components.input_color.reproduce_state import async_reproduce_states

# ----------------------------------------------------------------------
# Restore: the most dangerous gap. Hex state is lossy; only the extra_data
# carries kind/kelvin/xy-precision. A regression that drops any of these
# during the restore round-trip would never be caught by hex-state checks.
# ----------------------------------------------------------------------


async def test_restore_round_trip_preserves_white_kind_and_kelvin(
    hass: HomeAssistant,
) -> None:
    entity_id = "input_color.couch_color"
    extra = {
        "version": STATE_SCHEMA_VERSION,
        "xy": [0.4341, 0.4036],  # 2700K-ish Planckian xy
        "kind": "white",
        "kelvin": 2700,
        "brightness": 180,
    }
    mock_restore_cache_with_extra_data(
        hass,
        [(State(entity_id, "#FFFFFF", {"kind": "white"}), extra)],
    )

    # Now create the entry. Title is slugified to "couch_color" so the
    # entity_id matches what we pre-populated.
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Couch Color",
        data={
            CONF_NAME: "Couch Color",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#000000",  # deliberately different from restored
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state is not None
    # kind/kelvin survived (not "chromatic" + derived McCamy)
    assert state.attributes[ATTR_KIND] == "white"
    assert state.attributes["color_temp_kelvin"] == 2700
    assert state.attributes["brightness"] == 180
    # xy preserved to 4 decimals (the round() in extra_state_attributes)
    assert state.attributes["xy_color"] == [0.4341, 0.4036]


async def test_restore_round_trip_with_malformed_extra_falls_back(
    hass: HomeAssistant,
) -> None:
    """A garbage extra_data payload should not crash; entity falls back to initial."""
    entity_id = "input_color.x"
    mock_restore_cache_with_extra_data(
        hass,
        [(State(entity_id, "#FFFFFF", {}), {"this": "is not valid"})],
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="X",
        data={
            CONF_NAME: "X",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FF0000",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Initial red survives; no exception.
    state = hass.states.get(entity_id)
    r, _g, _b = state.attributes["rgb_color"]
    assert r > 200


# ----------------------------------------------------------------------
# Reproduce-state hardening: scenes can include weird snapshots.
# ----------------------------------------------------------------------


async def _setup_entity(hass: HomeAssistant, title: str = "X") -> str:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=title,
        data={
            CONF_NAME: title,
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


async def test_reproduce_state_with_unavailable_skips_color_but_sets_brightness(
    hass: HomeAssistant,
) -> None:
    """If state.state isn't a valid hex, brightness should still apply."""
    entity_id = await _setup_entity(hass)
    snapshot = State(
        entity_id,
        "unavailable",
        {"kind": "chromatic", "brightness": 220},
    )
    # Must not raise.
    await async_reproduce_states(hass, [snapshot])
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state.attributes["brightness"] == 220


async def test_reproduce_state_omitting_brightness_attr_does_not_clear(
    hass: HomeAssistant,
) -> None:
    """Snapshot without the brightness attr should NOT clear existing brightness."""
    entity_id = await _setup_entity(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 150},
        blocking=True,
    )
    assert hass.states.get(entity_id).attributes["brightness"] == 150

    # Snapshot deliberately omits the brightness attribute.
    snapshot = State(entity_id, "#00FF00", {"kind": "chromatic"})
    await async_reproduce_states(hass, [snapshot])
    await hass.async_block_till_done()
    # Brightness should still be 150 — color updated but brightness untouched.
    assert hass.states.get(entity_id).attributes["brightness"] == 150


# ----------------------------------------------------------------------
# Options flow + reload listener: the path by which UI changes apply.
# ----------------------------------------------------------------------


async def test_options_flow_updates_icon_and_reloads_entity(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Icon Test",
        data={
            CONF_NAME: "Icon Test",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FFFFFF",
            CONF_ICON: "mdi:palette",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_id = next(
        s.entity_id for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")
    )
    assert hass.states.get(entity_id).attributes.get("icon") == "mdi:palette"

    # Walk the options flow.
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_ICON: "mdi:lightbulb"}
    )
    await hass.async_block_till_done()

    # Entry has new icon in options...
    assert entry.options[CONF_ICON] == "mdi:lightbulb"
    # ...and (via the update listener -> reload path) so does the entity.
    assert hass.states.get(entity_id).attributes.get("icon") == "mdi:lightbulb"


# ----------------------------------------------------------------------
# brightness=0 must round-trip through apply_to as 0, not None.
# ----------------------------------------------------------------------


async def test_brightness_zero_is_distinct_from_none_through_apply_to(
    hass: HomeAssistant,
) -> None:
    entity_id = await _setup_entity(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        {ATTR_ENTITY_ID: entity_id, FIELD_BRIGHTNESS: 0},
        blocking=True,
    )
    assert hass.states.get(entity_id).attributes["brightness"] == 0

    captured: list[dict[str, Any]] = []

    async def _capture(call):
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
    assert captured[0]["brightness"] == 0


# ----------------------------------------------------------------------
# Setting kelvin then a chromatic color must wipe the stored kelvin so
# downstream consumers don't see stale "this color was a white" intent.
# ----------------------------------------------------------------------


async def test_chromatic_override_clears_previous_kelvin(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "color_temp_kelvin": 2700},
        blocking=True,
    )
    assert hass.states.get(entity_id).attributes["kind"] == "white"
    assert hass.states.get(entity_id).attributes["color_temp_kelvin"] == 2700

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {ATTR_ENTITY_ID: entity_id, "hex_value": "#FF0000"},
        blocking=True,
    )
    state = hass.states.get(entity_id)
    assert state.attributes["kind"] == "chromatic"
    # Chromatic colors don't carry a kelvin — the previously-stored 2700
    # is gone, and we explicitly emit None rather than a McCamy guess.
    assert state.attributes["color_temp_kelvin"] is None


# ----------------------------------------------------------------------
# Empty target list: documented no-op, not an error or stray call.
# ----------------------------------------------------------------------


async def test_apply_to_with_empty_target_is_a_noop(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    captured: list[dict[str, Any]] = []

    async def _capture(call):
        captured.append(dict(call.data))

    hass.services.async_register("light", "turn_on", _capture)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_APPLY_TO,
        {ATTR_ENTITY_ID: entity_id, FIELD_LIGHTS: []},
        blocking=True,
    )
    assert captured == []


# ----------------------------------------------------------------------
# Service wrapper must strip targeting keys; otherwise a call like
# {entity_id, area_id, hex_value} would leak area_id into normalize().
# ----------------------------------------------------------------------


async def test_service_strips_targeting_keys(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    # area_id present alongside hex_value — must succeed.
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {
            ATTR_ENTITY_ID: entity_id,
            "area_id": "some_area",
            "hex_value": "#00FF00",
        },
        blocking=True,
    )
    _r, g, _b = hass.states.get(entity_id).attributes["rgb_color"]
    assert g > 200


# ----------------------------------------------------------------------
# set_color + brightness in one call should both apply (brightness is
# not part of the mutually-exclusive shape set).
# ----------------------------------------------------------------------


async def test_set_color_with_brightness_applies_both(hass: HomeAssistant) -> None:
    entity_id = await _setup_entity(hass)
    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_COLOR,
        {
            ATTR_ENTITY_ID: entity_id,
            "hex_value": "#0000FF",
            "brightness": 100,
        },
        blocking=True,
    )
    state = hass.states.get(entity_id)
    _r, _g, b = state.attributes["rgb_color"]
    assert b > 200
    assert state.attributes["brightness"] == 100


# ----------------------------------------------------------------------
# Initial brightness from config entry must flow into the entity.
# ----------------------------------------------------------------------


async def test_initial_brightness_from_config_entry(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Bright Init",
        data={
            CONF_NAME: "Bright Init",
            CONF_INITIAL_MODE: MODE_WHITE,
            CONF_INITIAL_KELVIN: 3000,
            CONF_INITIAL_BRIGHTNESS: 170,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_id = next(
        s.entity_id for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")
    )
    state = hass.states.get(entity_id)
    assert state.attributes["brightness"] == 170
    assert state.attributes["color_temp_kelvin"] == 3000
    assert state.attributes["kind"] == "white"


async def test_initial_brightness_garbage_is_safe(hass: HomeAssistant) -> None:
    """Non-int initial brightness from a corrupted entry must not crash setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Garbage",
        data={
            CONF_NAME: "Garbage",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
            CONF_INITIAL_COLOR: "#FFFFFF",
            CONF_INITIAL_BRIGHTNESS: "not-a-number",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_id = next(
        s.entity_id for s in hass.states.async_all() if s.entity_id.startswith(f"{DOMAIN}.")
    )
    assert hass.states.get(entity_id).attributes["brightness"] is None


# ----------------------------------------------------------------------
# Config-flow coerce: unknown shapes must default safely, not crash.
# (Pure unit test, no HA event loop needed.)
# ----------------------------------------------------------------------


def test_coerce_color_input_unexpected_types_fall_back() -> None:
    assert _coerce_color_input({"r": 1, "g": 2, "b": 3}) == DEFAULT_HEX
    assert _coerce_color_input([1, 2, 3, 4]) == DEFAULT_HEX
    assert _coerce_color_input(None) == DEFAULT_HEX


def test_coerce_color_input_passes_through_strings_and_triples() -> None:
    assert _coerce_color_input("#ABCDEF") == "#ABCDEF"
    assert _coerce_color_input([255, 128, 0]) == "#FF8000"
