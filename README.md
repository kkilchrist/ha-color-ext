# Color — Home Assistant helper

A reusable color value for Home Assistant. Each `color` is a color you
can store, edit, reference from automations, capture in scenes, and apply to
one or more lights. Think of it like `input_number` or `input_boolean`, but
the value is a color.

Installs as a custom integration via [HACS](https://hacs.xyz). Lives entirely
in `custom_components/color/` — no frontend bundle, just the standard
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
2. Search for "Color" in HACS → Integrations → Explore & Add
3. Install, then restart Home Assistant
4. Settings → Devices & Services → **Add Integration** → "Color"

Each color you want is one integration instance (one config entry per color).

### Manual

Copy `custom_components/color/` into `<config>/custom_components/`,
restart Home Assistant, and add the integration from the UI.

## Services

### `color.set_color`

Set the stored color. Provide exactly one of `hex_value`, `rgb_color`,
`hs_color`, `xy_color`, `color_temp_kelvin`, or `color_name`. Brightness is
optional and independent of the color shape.

```yaml
service: color.set_color
target:
  entity_id: color.couch_color
data:
  hex_value: "#FF8000"
```

```yaml
service: color.set_color
target:
  entity_id: color.evening_warm
data:
  color_temp_kelvin: 2700
  brightness: 180
```

### `color.set_brightness`

Set or clear the stored brightness. Pass `null` to clear.

```yaml
service: color.set_brightness
target:
  entity_id: color.couch_color
data:
  brightness: 200
```

### `color.apply_to`

Send the stored color to one or more lights. The dispatcher sends
`color_temp_kelvin` for whites and `xy_color` for chromatic colors; Home
Assistant's light integration converts to whatever `supported_color_modes`
each target advertises.

```yaml
service: color.apply_to
target:
  entity_id: color.couch_color
data:
  lights:
    - light.living_room_strip
    - light.ceiling_island
  override_brightness: false   # if true, also push the stored brightness
  # brightness: 200            # OR set an explicit per-call brightness
```

**Brightness precedence:**
1. Explicit `brightness` field wins (0-255) — useful when a script wants
   this color with a per-call brightness without touching stored state
   (e.g. workout intervals where each phase has its own brightness).
2. Else if `override_brightness: true` AND the color has a stored
   brightness, push the stored value.
3. Else: omit brightness — each target light keeps its current level.

### How `apply_to` works — exact behavior

The dispatcher is intentionally small: it picks one of two color shapes
based on `kind`, optionally adds brightness per the precedence above, and
sends one batched `light.turn_on` call. Home Assistant's light component
handles per-fixture conversion from there.

**What `apply_to` sends, given helper state + call options:**

| Helper kind | Stored brightness | Call `brightness` | Call `override_brightness` | `light.turn_on` payload |
|---|---|---|---|---|
| chromatic | any | absent | any | `xy_color: [x, y]` |
| chromatic | `null` | absent | `true` | `xy_color` (no brightness — nothing stored) |
| chromatic | `150` | absent | `false` | `xy_color` (override is off) |
| chromatic | `150` | absent | `true` | `xy_color`, `brightness: 150` |
| chromatic | any | `60` | any | `xy_color`, `brightness: 60` (explicit wins) |
| white(2700K) | `null` | absent | any | `color_temp_kelvin: 2700` |
| white(2700K) | `200` | absent | `true` | `color_temp_kelvin: 2700`, `brightness: 200` |
| white(2700K) | `200` | `60` | `true` | `color_temp_kelvin: 2700`, `brightness: 60` |

**What Home Assistant then does with our payload, per target light:**

| We send | Target's `supported_color_modes` | HA's behavior |
|---|---|---|
| `xy_color` | includes `xy` | passes through; Hue-style gamut clamp applies |
| `xy_color` | includes `rgb`, `rgbw`, or `rgbww` (no xy) | converts xy → sRGB internally |
| `xy_color` | includes `hs` only | converts xy → hs |
| `xy_color` | `color_temp` only (tunable-white bulb) | McCamy-approximates xy → kelvin; meaningful near the Planckian locus, arbitrary for saturated colors |
| `color_temp_kelvin` | includes `color_temp` | passes through; clamped to bulb's `min/max_color_temp_kelvin` |
| `color_temp_kelvin` | RGB/HS/XY only (no `color_temp`) | converts kelvin → Planckian-locus xy → target's preferred shape |

So a `kind=white` helper applied to a chromatic RGB strip yields the
Planckian-locus chromaticity for the chosen Kelvin — the right answer.
A `kind=chromatic` saturated red applied to a tunable-white bulb yields
a very-low McCamy kelvin, which is technically meaningless but is what
the user implicitly asked for. If you want stricter behavior, branch
in your automation on the helper's `kind` attribute before calling
`apply_to`.

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

Every accepted input shape round-trips exactly: the attribute matching the
shape you set echoes your input verbatim (a hex is only normalized to
uppercase). Set `hex_value`/`rgb_color`/`color_name` and `hex_color` and
`rgb_color` are the exact sRGB bytes; set `hs_color` or `xy_color` and that
attribute echoes your unrounded values. The remaining representations are
derived.

## Blueprints and examples

- **[blueprints/](blueprints/)** — one-click importable blueprints. Start with
  "Sync Color to Lights" for the most common pattern.
- **[examples/](examples/)** — raw YAML snippets for scripts, automations,
  and scenes. Includes a `demo_walkthrough.yaml` script that cycles a single
  color through every input shape with 2-second delays so you can see
  each one render.

## Composition with scenes — the underrated pattern

`color` composes with scenes; it doesn't compete with them. This is
the most useful pattern in the integration and worth understanding before
you build anything else.

The integration ships a `reproduce_state` hook, which means **scenes that
include an color entity snapshot its full canonical state** (kind,
xy, kelvin, brightness) — and restore it on `scene.turn_on`.

The composition that falls out:

| Layer | Holds | Mutable | Example |
|---|---|---|---|
| `color` helper | A named color you can edit | Yes | `color.favorite_blue` |
| `scene` | A frozen moment, including the helper's value | No (until you re-create it) | `scene.movie_night` |

A user-facing workflow that becomes natural:

1. **Edit the favorite** from a dashboard card or automation — the
   `color` is the named slot. Change it whenever.
2. **Capture a moment** with `scene.create snapshot_entities: [color.x, light.a, light.b]`. The scene now remembers the helper's value at capture time **and** the lights' state.
3. **Restore later** with `scene.turn_on` — both the helper and the lights
   snap back to what they were when you captured.

This is different from a static scene because the helper between captures
is editable: you can build a "Living Room — Evening" scene that includes
`color.living_room_color`, then later edit that helper to a new
favorite, then re-capture the scene to update the snapshot. The helper is
the *named handle*; the scene is the *frozen application*.

It's also the answer to "but scenes already do this" — they do, for
literal device states. `color` adds a *named, reusable color value*
that scenes can include alongside device states, without you having to
hardcode hex values in the scene YAML.

See `examples/scenes/scene_capture.yaml` for a concrete walk-through.

## Scene support (technical)

Internally we implement `async_reproduce_states` so `scene.create` /
`scene.turn_on` round-trip the helper's canonical state through restore
data — the lossy hex `state` is sufficient for chromatic colors, and the
`kind`/`color_temp_kelvin` attributes carry the white-temperature path.
Malformed snapshots (state=`unavailable`, missing brightness attr) are
tolerated — see `reproduce_state.py`.

## Reading the color in scripts and automations

The two most useful patterns:

```yaml
# Use the color in a light.turn_on directly. Robust to missing entity.
service: light.turn_on
data:
  entity_id: light.island
  rgb_color: "{{ state_attr('color.gym_work_color', 'rgb_color') | default([255, 0, 0]) }}"

# Same but with explicit brightness for this call only — no stored state.
service: color.apply_to
target:
  entity_id: color.gym_work_color
data:
  lights: [light.island]
  brightness: 255          # explicit; ignores stored brightness
```

Reads are exact: the state is the literal hex you set (for hex/rgb/name
inputs), and `hs_color`/`xy_color` echo those shapes unrounded when they were
the input.

```yaml
{{ states('color.x') }}
```

## Creating entries programmatically

The normal install flow is the UI (Settings → Devices & services → Add
Integration → "Color"). If you need to create entries from a script
or another integration, the ConfigEntry `data` dict shape is:

```python
{
    "name": "Couch Color",                # required, becomes entity title
    "initial_mode": "chromatic",          # or "white"
    "initial_color": "#FF8000",           # required if mode=chromatic; hex string
    "initial_kelvin": 4000,               # required if mode=white; int Kelvin
    "initial_brightness": 200,            # optional; 0-255
    "icon": "mdi:palette",                # optional; MDI icon string
}
```

Then start a config flow:
```python
result = await hass.config_entries.flow.async_init(
    "color",
    context={"source": "user"},
    data={...},  # not actually consumed at user step; flow walks steps
)
```

In practice most callers build entries via `MockConfigEntry`-like patterns
in tests, or simply prompt the user through the UI. See `config_flow.py`
for the multi-step shape; `const.py` for field names.

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
python3.13 -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/python -m pytest tests/
```

`custom_components/color/` is kept in sync with the version proposed for Home
Assistant core ([core#177605](https://github.com/home-assistant/core/pull/177605)).
Keep the diff against that branch small: the deliberate deltas are the
`apply_to` action, the manifest, and parenthesized `except` tuples (core
targets Python 3.14 and uses PEP 758 syntax that Python 3.13 rejects).

Unit tests cover the colorimetric normalizer; integration tests use
`pytest-homeassistant-custom-component` and exercise the full config-flow →
entity → service-call → reproduce_state path.

## License

Apache 2.0.
