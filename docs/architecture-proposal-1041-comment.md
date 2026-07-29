Following up on my earlier comment about the color-helper HACS integration: it's now been field-tested (thanks @Ltek and others), and I'd like to move this forward into core. Since my last comment I researched how core has handled helper integrations over the past few years and **updated the implementation to match core precedent** (domain renamed `input_color` → `color`, plus a new `color_params` attribute; details below). Below is a concrete architecture proposal. I've been working on this problem intermittently for multiple years, first with an `input_text` helper holding a color string, parsed in scripts at apply time, then as the purpose-built integration. I'm offering to do the core port, the frontend PR, docs, and ongoing code ownership.

## Prior art: this ask is a decade old

- **Oct 2016** — [Input color](https://community.home-assistant.io/t/input-color/5057): an `input_color` component with a hex picker, usable in templates and automations.
- **Dec 2020** — [Color Picker Helper](https://community.home-assistant.io/t/color-picker-helper/255516) (20+ replies with +1s through 2024): an independent color helper for WLED secondary colors, ESPHome RGB displays, dashboard colors, and reusable automation values. Documented workarounds include `input_number` triplets plus template sensors, and `input_text` holding raw RGB.
- **Apr 2022** — [RGB/Color Picker Helper](https://community.home-assistant.io/t/rgb-color-picker-helper/410714).
- **Mar 2024** — [frontend#20125, Favorite color profiles](https://github.com/home-assistant/frontend/discussions/20125) (still open): per-light `favorite_colors` exists in the entity registry but is unnamed, unshared, and has no service API; j9brown built [Scenery](https://github.com/j9brown/scenery) to partially fill the gap.
- **May 2026** — [input_color HACS release](https://community.home-assistant.io/t/input-color-store-a-color-as-an-ha-helper-entity/1011810), the implementation below.

The consistent pattern: users don't want another scene mechanism; they want a **value type**. A scene freezes a color into an application. A helper is a named handle whose value can change and be referenced everywhere.

## Proposed design

Domain `color`, `integration_type: helper`, `iot_class: calculated`, zero external dependencies.

**Data model.** The canonical stored value is minimal:

| Field | Meaning |
|---|---|
| `xy` | CIE 1931 chromaticity (the canonical color) |
| `kind` | `chromatic` \| `white`: was the intent a color or a color temperature |
| `kelvin` | Only when `kind: white`; preserves the exact CCT instead of round-tripping through xy |
| `brightness` | 0–255 or unset; independent of color |

RGB is fixture-dependent (the same tuple renders differently per gamut); xyY is device-independent and is what Hue and the light color pipeline use natively. The `kind` flag ensures tunable-white targets receive a true `color_temp_kelvin` rather than a lossy xy→CCT approximation. All other representations (`hex`, `rgb_color`, `hs_color`, `color_temp_kelvin`) are derived state attributes; state is the hex string, plus `source_hex` echoing the user's exact input when one existed.

**Services.**
- `color.set_color`: exactly one of `hex_value`, `rgb_color`, `hs_color`, `xy_color`, `color_temp_kelvin`, `color_name`; optional `brightness`.
- `color.set_brightness` / `color.clear_brightness`.
- (HACS-only) `color.apply_to`: convenience service issuing one batched `light.turn_on`; proposed to stay out of the core PR (see Design questions below).

**Scenes.** The helper implements `async_reproduce_states`, so `scene.create` with `snapshot_entities` freezes the helper's canonical state and `scene.turn_on` restores it. Helper = named mutable value; scene = frozen application of values.

**Persistence.** `RestoreEntity` + versioned `ExtraStoredData` with defensive deserialization. No custom `Store`.

## Scope of work (three PRs, all of which I'm committing to)

1. **home-assistant/core** — the integration. **The port is done and essentially PR-ready in my core fork: [`kkilchrist/ha_core_color_helper@color-helper`](https://github.com/kkilchrist/ha_core_color_helper/tree/color-helper)** ([diff vs dev](https://github.com/home-assistant/core/compare/dev...kkilchrist:ha_core_color_helper:color-helper)). Fully async and typed, no third-party deps, config flow + options flow, `icons.json`/`strings.json` with translated selector labels, `ServiceValidationError` with translation keys and schema-level exactly-one-of color validation, 56 tests on the core test harness (100% coverage on `config_flow.py`, `__init__.py`, and `reproduce_state.py`), and hassfest, ruff, and mypy-strict all passing. The branch is rebased onto current `dev`; I'll open the draft PR (plus the brands-repo icon PR) on a maintainer's go-ahead. The field-tested [HACS implementation](https://github.com/kkilchrist/ha-color-ext) remains available for anyone who wants to try it today.
2. **home-assistant/frontend** — add the domain to the Helpers picker (currently hardcoded) and a more-info dialog reusing the existing light color/CCT picker UI, per @Marconius6's suggestion above. A working Lit card prototype exists at [ha-color-ext-card](https://github.com/kkilchrist/ha-color-ext-card) as a design reference.
3. **home-assistant.io** — docs page including the emit/apply truth tables (what payload the helper sends per state, and how the light component maps it per `supported_color_modes`) plus the example automations/blueprints already written for the HACS release.

## Design questions

**`apply_to`: proposed to drop from the core PR, unless others prefer to keep it.** Core value-holder helpers are uniformly self-targeting (`input_number.set_value`, `counter.increment`, `timer.start`; none commands other entities). The domains that push state onto other entities are scene/group-shaped, not value holders, so `apply_to` inverts HA's layering. The branching concern is also smaller than it looks: `light.turn_on` already converts color parameters per target capability (kelvin→hs for color-only bulbs, xy→kelvin for CT-only bulbs, `homeassistant/components/light/__init__.py`). The helper now exposes a `color_params` attribute: a dict directly splattable into `light.turn_on` (`data: "{{ state_attr('color.evening_amber', 'color_params') }}"`) with zero branching, following the spirit of the existing `light.turn_on` `profile:` parameter (named entry from `light_profiles.csv` expanding to color+brightness). This is implemented and tested in the repo. A possible follow-up is letting `light.turn_on` accept a color-helper entity reference directly, keeping the verb on the light domain. That said, if maintainers or others here prefer to keep `apply_to` in core, it's already implemented; it stays in the HACS version regardless.

## Out of scope

**Per-light `favorite_colors`.** Favorites ([frontend#16592](https://github.com/home-assistant/frontend/pull/16592), 2023.6) live as unvalidated entity-registry options (`options.light.favorite_colors`) with no service API, and no core registry option today references other entities, so integrating them is out of scope for this proposal. Worth noting for the future, though: favorite colors could also use the color helper as their value type, with a favorite slot referencing a named `color` entity instead of a raw literal. That would deliver exactly the global, named color store that [frontend#20125](https://github.com/home-assistant/frontend/discussions/20125) asks for, but the bridging would need its own frontend RFC (dangling-reference cleanup, registry validation).

## Conclusions

I'm happy to put in the work to get this over the finish line (the core port, the frontend PR, docs, and ongoing code ownership) if I can get a commitment from one of the core maintainers that this is supported / supportable, and would be merged once feature complete.

---

*Disclosure: Claude (Fable 5) was used to help research the prior-art history and draft this proposal. The integration design and implementation decisions are mine.*
