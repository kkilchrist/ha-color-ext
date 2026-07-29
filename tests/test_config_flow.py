"""Config flow tests."""

from __future__ import annotations

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.color.const import (
    CONF_INITIAL_KELVIN,
    CONF_INITIAL_MODE,
    DOMAIN,
    MODE_CHROMATIC,
    MODE_WHITE,
)


@pytest.mark.asyncio
async def test_flow_chromatic_path(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: "Living Room Color",
            CONF_INITIAL_MODE: MODE_CHROMATIC,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "chromatic"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"initial_color": [255, 128, 0]},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room Color"
    assert result["data"]["initial_color"] == "#FF8000"


@pytest.mark.asyncio
async def test_flow_white_path(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: "Warm White",
            CONF_INITIAL_MODE: MODE_WHITE,
        },
    )
    assert result["step_id"] == "white"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_INITIAL_KELVIN: 2700},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_INITIAL_KELVIN] == 2700
    assert result["data"][CONF_INITIAL_MODE] == MODE_WHITE
