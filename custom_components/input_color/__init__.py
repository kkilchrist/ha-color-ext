"""The Input Color helper integration.

Each config entry produces exactly one `InputColorEntity`. The entity is added
to a single shared `EntityComponent` keyed by DOMAIN so services targeting
`input_color.*` resolve uniformly.

Two service entry points are exposed:
- entity services (`set_color`, `set_brightness`, `apply_to`) registered via
  `component.async_register_entity_service` for `entity_id` targeting
- standalone service handlers omitted; entity-service form covers all UI uses
  and matches how `light.turn_on` / `input_text.set_value` behave.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from .color_math import ColorInputError
from .const import (
    DOMAIN,
    FIELD_BRIGHTNESS,
    FIELD_COLOR_NAME,
    FIELD_HEX,
    FIELD_HS,
    FIELD_KELVIN,
    FIELD_LIGHTS,
    FIELD_OVERRIDE_BRIGHTNESS,
    FIELD_RGB,
    FIELD_XY,
    MAX_KELVIN,
    MIN_KELVIN,
    SERVICE_APPLY_TO,
    SERVICE_CLEAR_BRIGHTNESS,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_COLOR,
)
from .entity import InputColorEntity

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# Schemas mirror the shapes accepted by light.turn_on so users have muscle
# memory. Mutual exclusivity is enforced inside the entity normalizer.
_SET_COLOR_SCHEMA: dict[Any, Any] = {
    vol.Optional(FIELD_HEX): cv.string,
    vol.Optional(FIELD_RGB): vol.All(
        cv.ensure_list,
        vol.Length(min=3, max=3),
        [vol.All(vol.Coerce(int), vol.Range(min=0, max=255))],
    ),
    vol.Optional(FIELD_HS): vol.All(
        cv.ensure_list,
        vol.Length(min=2, max=2),
        [vol.Coerce(float)],
    ),
    vol.Optional(FIELD_XY): vol.All(
        cv.ensure_list,
        vol.Length(min=2, max=2),
        [vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0))],
    ),
    vol.Optional(FIELD_KELVIN): vol.All(vol.Coerce(int), vol.Range(min=MIN_KELVIN, max=MAX_KELVIN)),
    vol.Optional(FIELD_COLOR_NAME): cv.string,
    vol.Optional(FIELD_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
}

_SET_BRIGHTNESS_SCHEMA: dict[Any, Any] = {
    vol.Required(FIELD_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Range(min=0, max=255)),
}

_CLEAR_BRIGHTNESS_SCHEMA: dict[Any, Any] = {}

_APPLY_TO_SCHEMA: dict[Any, Any] = {
    vol.Required(FIELD_LIGHTS): vol.All(cv.ensure_list, [cv.entity_id]),
    vol.Optional(FIELD_OVERRIDE_BRIGHTNESS, default=False): cv.boolean,
}


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Register the entity component and entity services.

    Called once at integration load. HA guarantees a single invocation per
    process, and `EntityComponent.async_register_entity_service` is idempotent
    on the platform-side service registry, so re-entry would be safe — but
    that's not exercised in practice.
    """
    component: EntityComponent[InputColorEntity] = EntityComponent(_LOGGER, DOMAIN, hass)
    hass.data[DOMAIN] = component

    # Entity-service handlers receive the full ServiceCall when registered as
    # a callable (not a method-name string), so we read .data ourselves and
    # strip the entity-targeting keys that HA leaves in.
    _STRIP_KEYS = {"entity_id", "area_id", "device_id", "floor_id", "label_id"}

    def _color_shape(call: ServiceCall) -> dict[str, Any]:
        return {k: v for k, v in call.data.items() if k not in _STRIP_KEYS}

    async def _wrap_set_color(entity: InputColorEntity, call: ServiceCall) -> None:
        try:
            await entity.async_set_color(**_color_shape(call))
        except ColorInputError as err:
            raise HomeAssistantError(str(err)) from err

    async def _wrap_set_brightness(entity: InputColorEntity, call: ServiceCall) -> None:
        await entity.async_set_brightness(call.data[FIELD_BRIGHTNESS])

    async def _wrap_clear_brightness(entity: InputColorEntity, call: ServiceCall) -> None:
        await entity.async_set_brightness(None)

    async def _wrap_apply_to(entity: InputColorEntity, call: ServiceCall) -> None:
        await entity.async_apply_to(
            call.data[FIELD_LIGHTS],
            override_brightness=call.data.get(FIELD_OVERRIDE_BRIGHTNESS, False),
        )

    component.async_register_entity_service(SERVICE_SET_COLOR, _SET_COLOR_SCHEMA, _wrap_set_color)
    component.async_register_entity_service(
        SERVICE_SET_BRIGHTNESS, _SET_BRIGHTNESS_SCHEMA, _wrap_set_brightness
    )
    component.async_register_entity_service(
        SERVICE_CLEAR_BRIGHTNESS, _CLEAR_BRIGHTNESS_SCHEMA, _wrap_clear_brightness
    )
    component.async_register_entity_service(SERVICE_APPLY_TO, _APPLY_TO_SCHEMA, _wrap_apply_to)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Add one entity per config entry."""
    component: EntityComponent[InputColorEntity] = hass.data[DOMAIN]
    entity = InputColorEntity(entry)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await component.async_add_entities([entity])
    # Track the entity on the entry so unload can remove it cleanly.
    entry.runtime_data = entity
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    component: EntityComponent[InputColorEntity] = hass.data[DOMAIN]
    entity: InputColorEntity | None = getattr(entry, "runtime_data", None)
    if entity is None or entity.entity_id is None:
        return True
    await component.async_remove_entity(entity.entity_id)
    entry.runtime_data = None
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change so name/icon updates apply."""
    await hass.config_entries.async_reload(entry.entry_id)
