"""Config flow for the Color helper.

Each color is its own ConfigEntry. The flow runs once at create-time; users edit
name/icon via the options flow afterwards. The initial color itself is also
editable via the entity service `color.set_color` at runtime, so the
flow is intentionally minimal — pick a name, an initial color or kelvin, and
done.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_INITIAL_BRIGHTNESS,
    CONF_INITIAL_COLOR,
    CONF_INITIAL_KELVIN,
    CONF_INITIAL_MODE,
    DEFAULT_HEX,
    DEFAULT_KELVIN,
    DOMAIN,
    MAX_KELVIN,
    MIN_KELVIN,
    MODE_CHROMATIC,
    MODE_WHITE,
)

CONF_ICON = "icon"

_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Optional(CONF_ICON): selector.IconSelector(),
        vol.Required(CONF_INITIAL_MODE, default=MODE_CHROMATIC): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value=MODE_CHROMATIC, label="Chromatic color"),
                    selector.SelectOptionDict(value=MODE_WHITE, label="White (color temperature)"),
                ],
                mode=selector.SelectSelectorMode.LIST,
            )
        ),
    }
)


def _chromatic_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_INITIAL_COLOR,
                default=defaults.get(CONF_INITIAL_COLOR, DEFAULT_HEX),
            ): selector.ColorRGBSelector(),
            vol.Optional(
                CONF_INITIAL_BRIGHTNESS,
                description={"suggested_value": defaults.get(CONF_INITIAL_BRIGHTNESS)},
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=255, step=1, mode=selector.NumberSelectorMode.SLIDER
                )
            ),
        }
    )


def _white_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_INITIAL_KELVIN,
                default=defaults.get(CONF_INITIAL_KELVIN, DEFAULT_KELVIN),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_KELVIN,
                    max=MAX_KELVIN,
                    step=50,
                    unit_of_measurement="K",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_INITIAL_BRIGHTNESS,
                description={"suggested_value": defaults.get(CONF_INITIAL_BRIGHTNESS)},
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=255, step=1, mode=selector.NumberSelectorMode.SLIDER
                )
            ),
        }
    )


def _coerce_color_input(raw: Any) -> str:
    """ColorRGBSelector returns a [r, g, b] list; we store hex."""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (list, tuple)) and len(raw) == 3:
        r, g, b = (int(v) for v in raw)
        return f"#{r:02X}{g:02X}{b:02X}"
    return DEFAULT_HEX


class ColorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Two-step flow: pick mode, then pick the corresponding initial value."""

    VERSION = 1

    def __init__(self) -> None:
        self._stash: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=_MODE_SCHEMA)

        self._stash.update(user_input)
        if user_input[CONF_INITIAL_MODE] == MODE_WHITE:
            return await self.async_step_white()
        return await self.async_step_chromatic()

    async def async_step_chromatic(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="chromatic", data_schema=_chromatic_schema({}))
        return self._finalize(
            {
                **self._stash,
                CONF_INITIAL_COLOR: _coerce_color_input(user_input.get(CONF_INITIAL_COLOR)),
                CONF_INITIAL_BRIGHTNESS: user_input.get(CONF_INITIAL_BRIGHTNESS),
            }
        )

    async def async_step_white(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="white", data_schema=_white_schema({}))
        return self._finalize(
            {
                **self._stash,
                CONF_INITIAL_KELVIN: int(user_input[CONF_INITIAL_KELVIN]),
                CONF_INITIAL_BRIGHTNESS: user_input.get(CONF_INITIAL_BRIGHTNESS),
            }
        )

    def _finalize(self, data: dict[str, Any]) -> ConfigFlowResult:
        name = data[CONF_NAME]
        # Drop None brightness so the entity sees a clean dict.
        if data.get(CONF_INITIAL_BRIGHTNESS) is None:
            data.pop(CONF_INITIAL_BRIGHTNESS, None)
        return self.async_create_entry(title=name, data=data)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return ColorOptionsFlow(entry)


class ColorOptionsFlow(OptionsFlow):
    """Options flow lets the user change the icon after creation."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current_icon = self._entry.options.get(CONF_ICON) or self._entry.data.get(CONF_ICON)
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ICON,
                    description={"suggested_value": current_icon},
                ): selector.IconSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
