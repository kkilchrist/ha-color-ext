# Changelog

## 0.2.0

### Breaking change: the domain is now `color`, not `input_color`

Home Assistant reserves the `input_*` prefix for its original YAML-era helpers,
so getting this into core meant renaming the domain. That rename is in this
release, and it is not automatic:

- entity IDs change from `input_color.gym_work_color` to `color.gym_work_color`;
- **your helpers have to be recreated.** A config entry belongs to a domain, so
  there is no in-place migration path. Note down each helper's name, icon and
  color before upgrading, then add them again under Settings > Devices &
  services > Helpers > Color;
- every reference has to be updated: automations, scripts, scene definitions,
  dashboard cards, and blueprints. Search your config for `input_color.` and
  for the `input_color.` action names (`input_color.set_color` becomes
  `color.set_color`, and so on);
- after upgrading, check that `custom_components/input_color/` is gone. If HACS
  left it behind, delete it and restart, or Home Assistant will keep loading the
  old integration alongside the new one;
- delete the leftover `input_color.*` entities under Settings > Devices &
  services > Entities, filtering for unavailable ones. Because of the bug fixed
  below, any helper you deleted under 0.1.x also left an orphan there.

If you would rather not do this yet, staying on 0.1.0 is fine. The domain in
0.2.0 matches what is proposed for core, so migrating once now means no second
rename if the core PR lands.

### Synced with the core proposal

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
