# Changelog

## 0.2.0

Sync with the version proposed for Home Assistant core
([core#177605](https://github.com/home-assistant/core/pull/177605)), plus the
lifecycle fixes for the bugs reported on the forum thread.

### Fixed

- **Deleting a helper now deletes its entity.** 0.1.0 added the entity outside
  the config entry, so the entity registry never learned who owned it: removing
  the helper left an `unavailable` entity behind that no UI could clear, and
  recreating a helper with the same name produced a `..._2` twin — the reported
  "it creates two Helpers every time". Setup now runs through a config-entry
  platform, so the registry entry is owned by the entry and removed with it.
  Reported by @pieterb26 and @Marconius6.
- Renaming a helper in the UI now applies to the owned registry entry.
- Invalid input is rejected as a `ServiceValidationError` with a translated
  message instead of raising a bare `HomeAssistantError`.
- Overflowing or non-finite numbers (`1e400`, huge ints) are treated as
  malformed input everywhere they can enter: service schemas, the config flow,
  restored state, and scene reproduction.
- Scene reproduction no longer aborts other domains when a color payload is
  rejected.
- Pure black (`#000000`) is rejected in the config flow with a message pointing
  at brightness, instead of being stored as an unusable chromaticity.
- `hex_value` strips at most one leading `#`.

### Changed

- Services, strings, and icons now match the core proposal, including
  `clear_brightness` and the `color_params` attribute.
- `apply_to` is kept as a custom-integration-only extra. Core deliberately does
  not ship an action that commands other entities; there, the pattern is to
  splat `color_params` into `light.turn_on`. Existing automations keep working.
- Minimum Home Assistant version is 2025.2.0.

### Upgrading from 0.1.x

Existing helpers keep their entity IDs and stored colors. If you deleted a
helper under 0.1.x, its orphaned entity is still in the registry — remove it
under **Settings → Devices & Services → Entities** (filter for unavailable
entities). Do that before recreating a helper with the same name, or the new
one lands on `..._2`.

## 0.1.0

Initial release.
