# Input Color — Home Assistant helper

A reusable color value for Home Assistant. Each `input_color` is a color you
can store, edit, reference from automations, capture in scenes, and apply to
one or more lights. Think of it like `input_number` or `input_boolean`, but
the value is a color.

Installs as a custom integration via [HACS](https://hacs.xyz). Lives entirely
in `custom_components/input_color/` — no frontend bundle, just the standard
Home Assistant attribute display and service-call UI.

## Why this exists

There is no built-in way in Home Assistant to store a color that isn't bound
to a specific light. People want this for:

- **Cross-light scenes** — pick one favorite color and apply it to whichever
  lights are on, without hardcoding the value in each scene
- **UI-driven color selection** — a Lovelace color picker that doesn't have
  to point at a fake light
- **LED strip choreography** — separate the choice of color from the act of
  setting any particular zone
- **Nightlight / accent presets** — store both color and brightness as one
  named thing

See the [Home Assistant community thread][thread] for the long version.

[thread]: https://community.home-assistant.io/t/color-picker-helper/255516

## Data model

Each input color stores:

| Field | Type | Notes |
|---|---|---|
| `xy` | `(x, y)` | CIE 1931 chromaticity — the canonical color value |
| `kind` | `"chromatic"` \| `"white"` | How the user selected the color |
| `kelvin` | `int \| None` | Only set when `kind == "white"` |
| `brightness` | `0-255 \| None` | Independent of color; optional |

All other representations (hex, RGB, HS, kelvin-for-chromatic) are derived on
the fly from xy. State persists across restarts via `RestoreEntity`.

### Why xyY and not RGB?

RGB is fixture-dependent. The same `rgb(255, 0, 0)` is a different physical
red on a Hue Play, a LIFX A19, and a cheap WS2812 strip. CIE xy is a
device-independent chromaticity, which is what Hue itself stores for its
favorites and what makes `apply_to` work consistently across mixed-vendor
setups. The optional `kind == "white"` flag remembers when the user picked a
color temperature so that tunable-white targets get a real kelvin value
instead of a converted-then-reconverted xy.

## Installation

### HACS (recommended)

1. Add this repository as a custom HACS repository (category: Integration)
2. Search for "Input Color" in HACS → Integrations → Explore & Add
3. Install, then restart Home Assistant
4. Settings → Devices & Services → **Add Integration** → "Input Color"

Each color you want is one integration instance (one config entry per color).

### Manual

Copy `custom_components/input_color/` into `<config>/custom_components/`,
restart Home Assistant, and add the integration from the UI.

## Services

### `input_color.set_color`

Set the stored color. Provide exactly one of `hex_value`, `rgb_color`,
`hs_color`, `xy_color`, `color_temp_kelvin`, or `color_name`. Brightness is
optional and independent of the color shape.

```yaml
service: input_color.set_color
target:
  entity_id: input_color.couch_color
data:
  hex_value: "#FF8000"
```

```yaml
service: input_color.set_color
target:
  entity_id: input_color.evening_warm
data:
  color_temp_kelvin: 2700
  brightness: 180
```

### `input_color.set_brightness`

Set or clear the stored brightness. Pass `null` to clear.

```yaml
service: input_color.set_brightness
target:
  entity_id: input_color.couch_color
data:
  brightness: 200
```

### `input_color.apply_to`

Send the stored color to one or more lights. The dispatcher sends
`color_temp_kelvin` for whites and `xy_color` for chromatic colors; Home
Assistant's light integration converts to whatever `supported_color_modes`
each target advertises.

```yaml
service: input_color.apply_to
target:
  entity_id: input_color.couch_color
data:
  lights:
    - light.living_room_strip
    - light.ceiling_island
  override_brightness: false   # if true, also push the stored brightness
```

## Attributes

| Attribute | Description |
|---|---|
| `state` | Hex color string (e.g. `"#FF8000"`) |
| `kind` | `"chromatic"` or `"white"` |
| `xy_color` | `[x, y]` chromaticity |
| `rgb_color` | `[r, g, b]` derived sRGB for display |
| `hs_color` | `[hue, saturation]` |
| `color_temp_kelvin` | Stored value when `kind == "white"`; `null` for chromatic colors |
| `brightness` | `0-255` or `null` |
| `hex_color` | Same as state, repeated for convenience |

## Scene support

Scenes can capture an input color and replay it. `scene.create` and
`scene.apply` both work; on replay we re-call `set_color` and `set_brightness`
to restore the snapshot.

## Limitations

- **Gamut clipping is per-fixture and invisible to the helper.** The swatch
  you see in the UI is sRGB. The light you apply it to has its own gamut
  triangle and may clip saturated cyans/greens. The helper passes the color
  through to `light.turn_on` and lets the light component clamp.
- **`color_temp_kelvin` is null for chromatic colors.** Only set when the
  user picked a white. When `apply_to` sends a chromatic color to a
  tunable-white target, HA's light component picks the closest representable
  white internally — that approximation lives in the light integration, not
  this helper.
- **No custom color picker UI yet.** v1 uses Home Assistant's built-in
  `color_rgb` selector in the config flow and the standard attribute display
  for the more-info panel. Custom Lovelace UI is on the roadmap.
- **Not in the Helpers picker.** Home Assistant's frontend hardcodes which
  domains appear under Settings → Helpers → Add Helper. Until that registry
  is patched, this integration appears under Settings → Devices & Services
  instead.

## Development

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/python -m pytest tests/
```

Unit tests cover the colorimetric normalizer; integration tests use
`pytest-homeassistant-custom-component` and exercise the full config-flow →
entity → service-call → reproduce_state path.

## License

Apache 2.0.
