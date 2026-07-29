Following up on my earlier comment about the color-helper HACS integration — it's now been field-tested (thanks @Ltek and others), and I'd like to move this forward into core. Since my last comment I researched how core has handled helper integrations over the past few years and **updated the implementation to match core precedent** (domain renamed `input_color` → `color`, new `color_params` attribute — details below). Below is a concrete architecture proposal. I've been working on this problem intermittently for multiple years — first with an `input_text` helper holding a color string, parsed in scripts at apply time, then as the purpose-built integration — and I'm offering to do the core port, the frontend PR, docs, and ongoing code ownership.

## Prior art — this ask is a decade old

- **Oct 2016** — [Input color](https://community.home-assistant.io/t/input-color/5057): an `input_color` component with a hex picker, usable in templates and automations.
- **Dec 2020** — [Color Picker Helper](https://community.home-assistant.io/t/color-picker-helper/255516) (20+ replies with +1s through 2024): an independent color helper for WLED secondary colors, ESPHome RGB displays, dashboard colors, and reusable automation values. Documented workarounds include `input_number` triplets plus template sensors, and `input_text` holding raw RGB.
- **Apr 2022** — [RGB/Color Picker Helper](https://community.home-assistant.io/t/rgb-color-picker-helper/410714).
- **Mar 2024** — [frontend#20125, Favorite color profiles](https://github.com/home-assistant/frontend/discussions/20125) (still open): per-light `favorite_colors` exists in the entity registry but is unnamed, unshared, and has no service API; j9brown built [Scenery](https://github.com/j9brown/scenery) to partially fill the gap.
- **May 2026** — [input_color HACS release](https://community.home-assistant.io/t/input-color-store-a-color-as-an-ha-helper-entity/1011810), the implementation below.

The consistent pattern: users don't want another scene mechanism — they want a **value type**. A scene freezes a color into an application; a helper is a named handle whose value can change and be referenced everywhere.

## Proposed design

Domain `color`, `integration_type: helper`, `iot_class: calculated`, zero external dependencies.

**Data model.** The canonical stored value is minimal:

| Field | Meaning |
|---|---|
| `xy` | CIE 1931 chromaticity — the canonical color |
| `kind` | `chromatic` \| `white` — was the intent a color or a color temperature |
| `kelvin` | Only when `kind: white`; preserves the exact CCT instead of round-tripping through xy |
| `brightness` | 0–255 or unset; independent of color |

RGB is fixture-dependent (the same tuple renders differently per gamut); xyY is device-independent and is what Hue and the light color pipeline use natively. The `kind` flag ensures tunable-white targets receive a true `color_temp_kelvin` rather than a lossy xy→CCT approximation. All other representations (`hex`, `rgb_color`, `hs_color`, `color_temp_kelvin`) are derived state attributes; state is the hex string, plus `source_hex` echoing the user's exact input when one existed.

**Services.**
- `color.set_color` — exactly one of `hex_value`, `rgb_color`, `hs_color`, `xy_color`, `color_temp_kelvin`, `color_name`; optional `brightness`.
- `color.set_brightness` / `color.clear_brightness`.
- (HACS-only) `color.apply_to` — convenience service issuing one batched `light.turn_on`; proposed to stay out of the core PR — see question 3 below.

**Scenes.** The helper implements `async_reproduce_states`, so `scene.create` with `snapshot_entities` freezes the helper's canonical state and `scene.turn_on` restores it. Helper = named mutable value; scene = frozen application of values.

**Persistence.** `RestoreEntity` + versioned `ExtraStoredData` with defensive deserialization. No custom `Store`.

## Scope of work (three PRs, all of which I'm committing to)

1. **home-assistant/core** — the integration. The [HACS implementation](https://github.com/kkilchrist/ha-color-ext) is already close to core shape: fully async, typed, no blocking I/O, no third-party deps, config flow + options flow, `strings.json`, 53 tests on the HA test harness covering color math, services, restore, and scene reproduction. Known port work: manifest cleanup, `icons.json`, service-schema validation via `vol.Exclusive` with `ServiceValidationError` translation keys, full config-flow error/abort coverage, core ruff/mypy-strict conformance, `quality_scale.yaml`.
2. **home-assistant/frontend** — add the domain to the Helpers picker (currently hardcoded) and a more-info dialog reusing the existing light color/CCT picker UI, per @Marconius6's suggestion above. A working Lit card prototype exists at [ha-color-ext-card](https://github.com/kkilchrist/ha-color-ext-card) as a design reference.
3. **home-assistant.io** — docs page including the emit/apply truth tables (what payload the helper sends per state, and how the light component maps it per `supported_color_modes`) plus the example automations/blueprints already written for the HACS release.

## Design questions — with proposed answers from core precedent

1. **Domain name: `color`, not `input_color` — already renamed.** No new `input_*` domain has been added since `input_button` ([core#62008](https://github.com/home-assistant/core/pull/62008), 2021.12). The one `input_*` domain proposed since — [`input_timetable`](https://github.com/home-assistant/architecture/discussions/751) — was closed by frenck in favor of the plain-named `schedule` integration. And `schedule` itself (2022.9, [core#76566](https://github.com/home-assistant/core/pull/76566)) shows that even storage-collection helpers now get unprefixed domain names. The integration has been renamed to `color` accordingly (open to bikeshedding).
2. **Config-entry pattern: keep it.** Every helper added or converted since 2022 other than `schedule` (`template`, `derivative`, `threshold`, `tod`, `switch_as_x`, `statistics`, `history_stats`, `trend`, `random`, `mold_indicator`, `generic_hygrostat`, …) is `config_flow: true`; the official scaffold (`script/scaffold/templates/config_flow_helper/`) only generates config-flow helpers; and current maintainer guidance (e.g. the [2025-07-18 dev blog on helpers linking to devices](https://developers.home-assistant.io/blog/2025/07/18/updated-pattern-for-helpers-linking-to-devices/)) is written entirely in terms of helper config entries. The implementation already matches this.
3. **`apply_to`: drop it from the core PR — replacement already implemented.** Core value-holder helpers are uniformly self-targeting (`input_number.set_value`, `counter.increment`, `timer.start` — none command other entities); the domains that push state onto other entities are scene/group-shaped, not value holders, so `apply_to` inverts HA's layering. The branching concern is also smaller than it looks: `light.turn_on` already converts color parameters per target capability (kelvin→hs for color-only bulbs, xy→kelvin for CT-only bulbs, `homeassistant/components/light/__init__.py`). The helper now exposes a `color_params` attribute — a dict directly splattable into `light.turn_on` (`data: "{{ state_attr('color.evening_amber', 'color_params') }}"`) with zero branching, following the spirit of the existing `light.turn_on` `profile:` parameter (named entry from `light_profiles.csv` expanding to color+brightness). This is implemented and tested in the repo. A possible follow-up is letting `light.turn_on` accept a color-helper entity reference directly, keeping the verb on the light domain. (`apply_to` stays in the HACS version for convenience.)
4. **`favorite_colors`: separate follow-up, not part of this.** Per-light favorites ([frontend#16592](https://github.com/home-assistant/frontend/pull/16592), 2023.6) live as unvalidated entity-registry options (`options.light.favorite_colors`) with no service API, and no core registry option today references other entities — so pointing favorites at helper entities would be a novel pattern needing dangling-reference cleanup and its own frontend RFC. This helper is instead the *global, named* color store that [frontend#20125](https://github.com/home-assistant/frontend/discussions/20125) asks for; bridging the two can come later.

## Conclusions

I'm happy to put in the work to get this over the finish line — the core port, the frontend PR, docs, and ongoing code ownership — if I can get a commitment from one of the core maintainers that this is supported / supportable, and would be merged once feature complete.

---

*Disclosure: Claude (Fable 5) was used to help research the prior-art history and draft this proposal. The integration design and implementation decisions are mine.*
