# Blueprints

One-click-importable Home Assistant blueprints that wrap common
`color` patterns.

## Available

| Blueprint | What it does | Import URL |
|---|---|---|
| [Sync Color to Lights](automation/color_sync_to_lights.yaml) | Whenever an color changes, push the new value to one or more lights via `apply_to`. The most common pattern. | `https://github.com/kkilchrist/ha-color-ext/blob/main/blueprints/automation/color_sync_to_lights.yaml` |

## How to import

1. In Home Assistant, go to **Settings → Automations & Scenes → Blueprints**
2. Click **Import Blueprint** in the bottom-right
3. Paste the import URL from the table above
4. Click **Preview Blueprint**, then **Import Blueprint**
5. Use the blueprint via **Create Automation → Use Blueprint**

Each blueprint exposes its configuration inputs (which color, which
lights, etc.) in the standard HA UI — no YAML editing required.

## Want more?

Open an issue describing the pattern; if it's general enough we'll add it
here. For one-off uses, the `examples/` directory shows the raw YAML you
can copy-paste instead.
