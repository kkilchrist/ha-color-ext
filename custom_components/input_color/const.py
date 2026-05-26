"""Constants for the Input Color helper."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "input_color"

CONF_INITIAL_COLOR: Final = "initial_color"
CONF_INITIAL_BRIGHTNESS: Final = "initial_brightness"
CONF_INITIAL_KELVIN: Final = "initial_kelvin"
CONF_INITIAL_MODE: Final = "initial_mode"

# Initial-mode selector values used by the config flow.
MODE_CHROMATIC: Final = "chromatic"
MODE_WHITE: Final = "white"

# Internal "kind" of the stored color — chromatic (selected as a color) vs
# white (selected as a color temperature). This is what makes apply_to able to
# do the right thing for tunable-white targets.
KIND_CHROMATIC: Final = "chromatic"
KIND_WHITE: Final = "white"

ATTR_KIND: Final = "kind"
ATTR_XY_COLOR: Final = "xy_color"
ATTR_RGB_COLOR: Final = "rgb_color"
ATTR_HS_COLOR: Final = "hs_color"
ATTR_COLOR_TEMP_KELVIN: Final = "color_temp_kelvin"
ATTR_BRIGHTNESS: Final = "brightness"
ATTR_HEX_COLOR: Final = "hex_color"

# Service names.
SERVICE_SET_COLOR: Final = "set_color"
SERVICE_SET_BRIGHTNESS: Final = "set_brightness"
SERVICE_CLEAR_BRIGHTNESS: Final = "clear_brightness"
SERVICE_APPLY_TO: Final = "apply_to"

# set_color service field names.
FIELD_HEX: Final = "hex_value"
FIELD_RGB: Final = "rgb_color"
FIELD_HS: Final = "hs_color"
FIELD_XY: Final = "xy_color"
FIELD_KELVIN: Final = "color_temp_kelvin"
FIELD_COLOR_NAME: Final = "color_name"
FIELD_BRIGHTNESS: Final = "brightness"

# apply_to service field names.
# `lights` (not `target`) avoids visual collision with HA's top-level
# `target:` block in service-call YAML and the visual editor.
FIELD_LIGHTS: Final = "lights"
FIELD_OVERRIDE_BRIGHTNESS: Final = "override_brightness"

# Defaults (CIE D65 white-ish — pure white sRGB lands here).
DEFAULT_KELVIN: Final = 4000
DEFAULT_HEX: Final = "#FFFFFF"

# Kelvin range we accept on input. Targets clamp to their own min/max.
MIN_KELVIN: Final = 1000
MAX_KELVIN: Final = 20000

# Storage key for restored state on a per-entity basis is managed by
# RestoreEntity; we just track the schema version here for serialization.
STATE_SCHEMA_VERSION: Final = 1
