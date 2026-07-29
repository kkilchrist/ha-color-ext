# Examples

Raw YAML snippets demonstrating common `color` patterns. Copy what you
need into your Home Assistant configuration.

For one-click installable versions, see the [blueprints](../blueprints/).

## Layout

```
examples/
├── scripts/
│   └── demo_walkthrough.yaml      Cycle through every input shape with delays
├── automations/
│   ├── sync_one_to_one.yaml       Simplest: one color drives one light
│   └── tap_to_apply_favorite.yaml Button helper triggers a saved preset
└── scenes/
    └── scene_capture.yaml         scene.create snapshot including color
```

## Quick reference

### Set the color from an automation or script

```yaml
- service: color.set_color
  target:
    entity_id: color.your_color
  data:
    hex_value: "#FF8000"   # or rgb_color, hs_color, xy_color, color_temp_kelvin, color_name
```

Exactly one shape per call. Brightness is independent and optional:

```yaml
- service: color.set_color
  target:
    entity_id: color.your_color
  data:
    hex_value: "#FF8000"
    brightness: 200
```

### Push the stored color to lights

```yaml
- service: color.apply_to
  target:
    entity_id: color.your_color
  data:
    lights:
      - light.lamp_one
      - light.lamp_two
    override_brightness: false
```

`override_brightness: true` includes the stored brightness in the
`light.turn_on` call; `false` leaves each light at its current brightness.

### Read the color in templates

```yaml
{{ states('color.your_color') }}                       # "#FF8000"
{{ state_attr('color.your_color', 'rgb_color') }}      # [255, 128, 0]
{{ state_attr('color.your_color', 'hs_color') }}       # [30, 100]
{{ state_attr('color.your_color', 'kind') }}           # "chromatic" or "white"
{{ state_attr('color.your_color', 'color_temp_kelvin') }}  # int or null
```

## Got a pattern you want to share?

Open a PR adding it to the relevant `examples/` subfolder, with a comment
explaining the use case and any setup steps.
