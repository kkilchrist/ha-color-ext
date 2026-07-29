"""Entity class for the Color helper."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import light
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers.restore_state import ExtraStoredData, RestoreEntity

from .color_math import (
    CanonicalColor,
    ColorInputError,
    compute_source_hex,
    derive_hex,
    derive_hs,
    derive_kelvin,
    derive_rgb,
    normalize,
)
from .const import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_PARAMS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HEX_COLOR,
    ATTR_HS_COLOR,
    ATTR_KIND,
    ATTR_RGB_COLOR,
    ATTR_SOURCE_HEX,
    ATTR_XY_COLOR,
    CONF_INITIAL_BRIGHTNESS,
    CONF_INITIAL_COLOR,
    CONF_INITIAL_KELVIN,
    CONF_INITIAL_MODE,
    DEFAULT_HEX,
    DEFAULT_KELVIN,
    FIELD_HEX,
    FIELD_KELVIN,
    KIND_WHITE,
    MODE_WHITE,
    STATE_SCHEMA_VERSION,
)

_LOGGER = logging.getLogger(__name__)


class _StoredColor(ExtraStoredData):
    """Restore payload preserving canonical precision across restarts."""

    def __init__(
        self,
        canonical: CanonicalColor,
        brightness: int | None,
        source_hex: str | None = None,
    ) -> None:
        self.canonical = canonical
        self.brightness = brightness
        self.source_hex = source_hex

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": STATE_SCHEMA_VERSION,
            "xy": list(self.canonical.xy),
            "kind": self.canonical.kind,
            "kelvin": self.canonical.kelvin,
            "brightness": self.brightness,
            "source_hex": self.source_hex,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> _StoredColor | None:
        try:
            xy = data["xy"]
            kind = data["kind"]
            canonical = CanonicalColor(
                xy=(float(xy[0]), float(xy[1])),
                kind=str(kind),
                kelvin=int(data["kelvin"]) if data.get("kelvin") is not None else None,
            )
            brightness = data.get("brightness")
            if brightness is not None:
                brightness = int(brightness)
            source_hex = data.get("source_hex")
            if source_hex is not None:
                source_hex = str(source_hex)
        except (KeyError, TypeError, ValueError):
            return None
        return cls(canonical, brightness, source_hex)


class ColorEntity(RestoreEntity):
    """A color value with multiple representations and an apply-to dispatcher."""

    _attr_should_poll = False
    _attr_has_entity_name = False

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        # Name is derived dynamically from entry.title so UI renames apply
        # without requiring an integration reload.
        self._canonical: CanonicalColor = self._initial_canonical(entry)
        self._brightness: int | None = self._initial_brightness(entry)
        self._source_hex: str | None = self._initial_source_hex(entry)

    @property
    def name(self) -> str | None:
        return self._entry.title or self._entry.data.get("name")

    @property
    def icon(self) -> str | None:
        return self._entry.options.get("icon") or self._entry.data.get("icon")

    # ---- initialization helpers ------------------------------------------

    @staticmethod
    def _initial_canonical(entry: ConfigEntry) -> CanonicalColor:
        mode = entry.data.get(CONF_INITIAL_MODE)
        if mode == MODE_WHITE:
            kelvin = entry.data.get(CONF_INITIAL_KELVIN, DEFAULT_KELVIN)
            try:
                return normalize({FIELD_KELVIN: kelvin})
            except ColorInputError:
                return normalize({FIELD_KELVIN: DEFAULT_KELVIN})

        initial = entry.data.get(CONF_INITIAL_COLOR, DEFAULT_HEX)
        try:
            return normalize({FIELD_HEX: initial})
        except ColorInputError:
            return normalize({FIELD_HEX: DEFAULT_HEX})

    @staticmethod
    def _initial_source_hex(entry: ConfigEntry) -> str | None:
        """Compute source_hex from the initial config (or None for white-init)."""
        mode = entry.data.get(CONF_INITIAL_MODE)
        if mode == MODE_WHITE:
            return None
        initial = entry.data.get(CONF_INITIAL_COLOR)
        if not initial:
            return None
        return compute_source_hex({FIELD_HEX: initial})

    @staticmethod
    def _initial_brightness(entry: ConfigEntry) -> int | None:
        b = entry.data.get(CONF_INITIAL_BRIGHTNESS)
        if b is None:
            return None
        try:
            value = int(b)
        except (TypeError, ValueError):
            return None
        return max(0, min(255, value))

    # ---- properties -------------------------------------------------------

    @property
    def state(self) -> str:
        return derive_hex(self._canonical)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        x, y = self._canonical.xy
        r, g, b = derive_rgb(self._canonical)
        h, s = derive_hs(self._canonical)
        return {
            ATTR_KIND: self._canonical.kind,
            ATTR_XY_COLOR: [round(x, 4), round(y, 4)],
            ATTR_RGB_COLOR: [r, g, b],
            ATTR_HS_COLOR: [round(h, 2), round(s, 2)],
            ATTR_COLOR_TEMP_KELVIN: derive_kelvin(self._canonical),
            ATTR_BRIGHTNESS: self._brightness,
            ATTR_HEX_COLOR: derive_hex(self._canonical),
            ATTR_SOURCE_HEX: self._source_hex,
            ATTR_COLOR_PARAMS: self._color_params(),
        }

    def _color_params(self) -> dict[str, Any]:
        """Payload splattable directly into light.turn_on.

        `{"xy_color": [x, y]}` for chromatic, `{"color_temp_kelvin": k}` for
        white, plus `"brightness"` when one is stored (matching light-profile
        semantics, where a profile carries color and brightness together).
        The light component converts per-target capability, so consumers
        never branch on kind or fixture support:

            data: "{{ state_attr('color.evening_amber', 'color_params') }}"
        """
        if self._canonical.kind == KIND_WHITE and self._canonical.kelvin is not None:
            params: dict[str, Any] = {light.ATTR_COLOR_TEMP_KELVIN: self._canonical.kelvin}
        else:
            x, y = self._canonical.xy
            params = {light.ATTR_XY_COLOR: [x, y]}
        if self._brightness is not None:
            params[light.ATTR_BRIGHTNESS] = self._brightness
        return params

    # ---- restore ---------------------------------------------------------

    @property
    def extra_restore_state_data(self) -> ExtraStoredData | None:
        return _StoredColor(self._canonical, self._brightness, self._source_hex)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_extra = await self.async_get_last_extra_data()
        if last_extra is not None:
            stored = _StoredColor.from_dict(last_extra.as_dict())
            if stored is not None:
                self._canonical = stored.canonical
                self._brightness = stored.brightness
                self._source_hex = stored.source_hex

    # ---- setters --------------------------------------------------------

    async def async_set_color(self, **shape: Any) -> None:
        """Set the color from any one accepted input shape."""
        # Defensive copy: don't mutate caller's kwargs dict.
        color_shape = dict(shape)
        brightness = color_shape.pop(ATTR_BRIGHTNESS, None)
        self._canonical = normalize(color_shape)
        # source_hex tracks the user's literal input when it had a hex
        # equivalent (hex/rgb/hs/color_name). For xy/kelvin inputs it becomes
        # None, which is the right semantic: there's no "source hex" for
        # those — the user picked a chromaticity or a kelvin, not a color.
        self._source_hex = compute_source_hex(color_shape)
        if brightness is not None:
            self._brightness = max(0, min(255, int(brightness)))
        self.async_write_ha_state()

    async def async_set_brightness(self, brightness: int | None) -> None:
        """Set or clear the stored brightness (null clears it)."""
        if brightness is None:
            self._brightness = None
        else:
            self._brightness = max(0, min(255, int(brightness)))
        self.async_write_ha_state()

    # ---- apply dispatcher -----------------------------------------------

    async def async_apply_to(
        self,
        target_entity_ids: list[str],
        override_brightness: bool = False,
        brightness: int | None = None,
    ) -> None:
        """Apply this color to one or more lights via light.turn_on.

        Sends `color_temp_kelvin` for whites and `xy_color` for chromatic.
        HA's own light component handles per-fixture conversion to whatever
        `supported_color_modes` the target actually advertises. We make a
        single batched service call so HA fans out per-light failures
        independently rather than fail-stopping on the first error.

        Brightness precedence (so apply_to stays the canonical entry point
        even when the caller wants a one-off value):
        1. Explicit `brightness` argument wins if provided (0-255).
        2. Else if `override_brightness=True` AND a brightness is stored on
           this entity, push the stored value.
        3. Else: omit brightness — each target light keeps its current level.
        """
        if not target_entity_ids:
            return

        if self._canonical.kind == KIND_WHITE and self._canonical.kelvin is not None:
            color_data: dict[str, Any] = {light.ATTR_COLOR_TEMP_KELVIN: self._canonical.kelvin}
        else:
            x, y = self._canonical.xy
            color_data = {light.ATTR_XY_COLOR: [x, y]}

        if brightness is not None:
            color_data[light.ATTR_BRIGHTNESS] = max(0, min(255, int(brightness)))
        elif override_brightness and self._brightness is not None:
            color_data[light.ATTR_BRIGHTNESS] = self._brightness

        await self.hass.services.async_call(
            light.DOMAIN,
            light.SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: list(target_entity_ids), **color_data},
            blocking=True,
            context=self._context,
        )
