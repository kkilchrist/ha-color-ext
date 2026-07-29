# Architecture proposal: `input_color` — a color helper entity for Home Assistant core

<!-- Draft for posting to github.com/orgs/home-assistant/discussions (or home-assistant/architecture).
     Working implementation: https://github.com/kkilchrist/ha-color-ext -->

## Summary

Add a first-class **color helper** to Home Assistant core: an entity that stores a color
(chromatic or white/color-temperature, with optional brightness) as a named, mutable,
restorable value — the way `input_number` stores a number or `input_datetime` stores a
time. A field-tested implementation already exists as a HACS custom integration
(`input_color`, [ha-color-ext](https://github.com/kkilchrist/ha-color-ext)). This is a
problem I've been working on intermittently for multiple years — first with an
`input_text` helper holding the color string, parsed in scripts at apply time, then as
a purpose-built integration — and I'm
offering to do the work to bring it into core, including the companion frontend and
docs PRs.

## The problem

There is no way in Home Assistant to name a color and reuse it. Users who want
"our warm evening amber" or "kid's nightlight teal" applied across several lights must
hardcode RGB tuples in every automation and scene, or build fragile workarounds. The
demand for this has been continuous for nearly a decade:

- **Oct 2016** — [Input color](https://community.home-assistant.io/t/input-color/5057)
  (Feature Requests): an `input_color` component with a hex picker, usable in templates
  and automations.
- **Dec 2020** — [Color Picker Helper](https://community.home-assistant.io/t/color-picker-helper/255516)
  (Feature Requests, 20+ replies with +1s through 2024): an independent color helper not
  tied to any light, for WLED secondary colors, ESPHome RGB displays, dashboard colors,
  and reusable automation values. Documented workarounds include three `input_number`
  helpers plus template sensors to reassemble hex/RGB, and `input_text` holding raw RGB —
  both of which lose visual selection and type safety.
- **Apr 2022** — [RGB/Color Picker Helper](https://community.home-assistant.io/t/rgb-color-picker-helper/410714)
  (Feature Requests): the same ask, framed around visually indicating colors for RGB lights.
- **Mar 2024** — [Favorite color profiles](https://github.com/home-assistant/frontend/discussions/20125)
  (frontend discussion, still open): save named color profiles reusable across lights.
  Commenters note `favorite_colors` already exists in the entity registry but is
  per-light, has no service to modify it, and can't be named or shared. j9brown later
  built the third-party [Scenery](https://github.com/j9brown/scenery) integration to
  partially fill this gap.
- **2024–2026** — [Color Helper Entity](https://github.com/orgs/home-assistant/discussions/1041)
  (org discussion): consolidates the ask; recent comments include LIFX users hardcoding
  nightlight colors (elpeterson), system-status color use cases (ChrisE2018), and a
  suggestion to reuse the existing light color UI for the helper (Marconius6).
- **May 2026** — [input_color HACS release](https://community.home-assistant.io/t/input-color-store-a-color-as-an-ha-helper-entity/1011810):
  the implementation this proposal is based on, with positive field testing reported in
  discussion #1041.

The pattern across all of these: users don't want another scene mechanism — they want a
**value type**. Scenes freeze a color into an application; a helper is a named handle
whose value can change and be referenced everywhere.

## Proposed design

Domain: `input_color` (open to naming feedback — see Open questions), registered as an
`integration_type: helper`, `iot_class: calculated`, zero external dependencies.

### Data model

The canonical stored value is deliberately minimal:

| Field | Meaning |
|---|---|
| `xy` | CIE 1931 chromaticity — the canonical color |
| `kind` | `chromatic` \| `white` — whether the user's intent was a color or a color temperature |
| `kelvin` | Only when `kind: white`; preserves the exact CCT rather than round-tripping through xy |
| `brightness` | 0–255 or unset; independent of color |

Rationale: RGB is fixture-dependent (the same RGB renders differently per gamut), while
xyY is device-independent and is what Hue and the light component's color pipeline use
natively. The `kind` flag exists so tunable-white targets receive a true
`color_temp_kelvin` instead of a lossy xy→CCT approximation. All other representations
(`hex`, `rgb_color`, `hs_color`, `color_temp_kelvin`) are derived and exposed as state
attributes; state is the hex string, plus a `source_hex` attribute echoing the user's
exact input when one existed.

### Services

- `input_color.set_color` — accepts exactly one of `hex_value`, `rgb_color`, `hs_color`,
  `xy_color`, `color_temp_kelvin`, `color_name`; optional `brightness`.
- `input_color.set_brightness` / `input_color.clear_brightness`.
- `input_color.apply_to` — convenience service issuing one batched `light.turn_on` with
  `xy_color` (chromatic) or `color_temp_kelvin` (white), with documented brightness
  precedence (explicit field > stored-with-override > omitted). Everything it does is
  also achievable by templating the helper's attributes into `light.turn_on`, so it can
  be dropped from the core PR if reviewers prefer a smaller surface.

### Scene integration

The helper implements `async_reproduce_states`, so `scene.create` with
`snapshot_entities` freezes the helper's canonical state and `scene.turn_on` restores
it. This gives a clean division of labor: **helper = named mutable value, scene = frozen
application of values** — and directly answers the "why not just use scenes" question
from the forum threads.

### Persistence

`RestoreEntity` + versioned `ExtraStoredData` (schema-versioned dict with defensive
deserialization). No custom `Store`.

## Alternatives considered

- **Per-light `favorite_colors`** (entity registry): exists today, but per-light,
  unnamed, and has no service API (frontend#20125). Complements rather than replaces a
  shared helper.
- **Scenes**: freeze color *into* specific lights; can't be referenced as a value,
  can't be templated, and changing "our amber" means editing every scene.
- **Scenery (custom)**: YAML-defined named scenes/colors; closer, but still
  application-shaped rather than a value entity, and not a helper non-technical users
  can create from the UI.
- **input_text / input_number triplets + templates**: the current documented workaround;
  no validation, no picker, no color-space correctness.

## Scope of work (three PRs)

1. **home-assistant/core** — the `input_color` integration. The HACS implementation is
   already close to core shape: fully async, typed, no blocking I/O, no third-party
   deps, config flow + options flow, `strings.json`, 48 tests on the HA test harness
   covering color math, services, restore, and scene reproduction. Known port work:
   manifest cleanup, `icons.json`, service-schema validation via `vol.Exclusive` with
   `ServiceValidationError` translation keys, full config-flow error/abort coverage,
   core ruff/mypy-strict conformance, `quality_scale.yaml`.
2. **home-assistant/frontend** — add the domain to the Helpers picker (currently
   hardcoded), and a more-info dialog reusing the existing light color/CCT picker UI
   (per Marconius6's suggestion in #1041). A working Lit-based card prototype exists at
   [ha-color-ext-card](https://github.com/kkilchrist/ha-color-ext-card) as a design
   reference.
3. **home-assistant.io** — integration docs page, including the emit/apply truth tables
   (what payload the helper sends per state, and how the light component maps it per
   `supported_color_modes`) and example automations/blueprints already written for the
   HACS release.

## Design questions — with proposed answers from core precedent

1. **Domain name: propose `color`, not `input_color`.** No new `input_*` domain has
   been added since `input_button` ([core#62008](https://github.com/home-assistant/core/pull/62008),
   2021.12). The one proposed since — [`input_timetable`](https://github.com/home-assistant/architecture/discussions/751) —
   was closed by frenck in favor of the plain-named `schedule` integration, and
   `schedule` itself (2022.9, [core#76566](https://github.com/home-assistant/core/pull/76566))
   shows even storage-collection helpers now get unprefixed names. The HACS version
   keeps `input_color`; the core PR should use `color` (open to bikeshedding).
2. **Config-entry pattern: keep it.** Every helper added or converted since 2022 other
   than `schedule` is `config_flow: true`; the official scaffold
   (`script/scaffold/templates/config_flow_helper/`) only generates config-flow
   helpers; and current maintainer guidance (e.g. the
   [2025-07-18 dev blog on helpers linking to devices](https://developers.home-assistant.io/blog/2025/07/18/updated-pattern-for-helpers-linking-to-devices/))
   is written entirely in terms of helper config entries.
3. **`apply_to`: drop it from the core PR.** Core value-holder helpers are uniformly
   self-targeting; only scene/group-shaped domains push state onto other entities, so
   `apply_to` inverts HA's layering. `light.turn_on` already converts color parameters
   per target capability, so instead the helper will expose a `color_params` attribute —
   a dict directly splattable into `light.turn_on`
   (`data: "{{ state_attr('color.evening_amber', 'color_params') }}"`), following the
   spirit of `light.turn_on`'s existing `profile:` parameter. A possible follow-up is
   letting `light.turn_on` accept a color-helper entity reference directly. (`apply_to`
   stays in the HACS version.)
4. **`favorite_colors`: separate follow-up.** Per-light favorites
   ([frontend#16592](https://github.com/home-assistant/frontend/pull/16592), 2023.6)
   are unvalidated entity-registry options with no service API, and no registry option
   today references other entities — bridging them to helper entities needs its own
   RFC. This helper is instead the global, named color store that
   [frontend#20125](https://github.com/home-assistant/frontend/discussions/20125)
   asks for.

## Why now

The demand is documented and ten years old; a complete, tested implementation exists and
has positive field reports. I've been chipping away at this problem intermittently for
several years, and the maintainer (me, @kkilchrist) is committed to doing the core port,
frontend PR, docs, and ongoing code ownership.

---

*Disclosure: Claude (Fable 5) was used to help research the prior-art history and draft
this proposal. The integration design and implementation decisions are mine.*
