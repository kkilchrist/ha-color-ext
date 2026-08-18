"""Regression tests for the helper lifecycle bugs reported against 0.1.0.

0.1.0 added the entity through a bare ``EntityComponent.async_add_entities``
call, so its registry entry was never linked to the config entry. Two things
followed, both reported by users on the forum thread:

* deleting the helper left the entity behind as a restored/unavailable row
  that nothing in the UI could remove;
* recreating a helper with the same name then landed on ``..._2``, which read
  as "it creates two helpers every time".

Setup now runs through a config-entry-backed platform, so the registry entry
is owned by the entry and removed with it.
"""

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.color.const import (
    CONF_INITIAL_COLOR,
    CONF_INITIAL_MODE,
    DOMAIN,
    MODE_CHROMATIC,
)

ENTITY_ID = "color.couch_color"


async def _add_couch_color(hass: HomeAssistant) -> MockConfigEntry:
    """Create and set up a helper named "Couch Color"."""
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
    return entry


async def test_entity_is_owned_by_its_config_entry(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """The registry entry is linked to the entry, so the UI can manage it."""
    entry = await _add_couch_color(hass)

    registry_entry = entity_registry.async_get(ENTITY_ID)
    assert registry_entry is not None
    assert registry_entry.config_entry_id == entry.entry_id


async def test_deleting_the_helper_removes_the_entity(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Removing the entry takes the registry entry and state with it."""
    entry = await _add_couch_color(hass)

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert entity_registry.async_get(ENTITY_ID) is None
    assert hass.states.get(ENTITY_ID) is None


async def test_recreating_after_delete_reuses_the_entity_id(
    hass: HomeAssistant,
) -> None:
    """No `_2` twin: the freed entity_id is available again."""
    entry = await _add_couch_color(hass)
    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    await _add_couch_color(hass)

    assert [s.entity_id for s in hass.states.async_all() if s.domain == DOMAIN] == [
        ENTITY_ID
    ]
