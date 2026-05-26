"""Color normalization for the Input Color helper.

The helper stores a canonical `(xy, kind, kelvin?)` tuple internally and derives
every attribute (hex/rgb/hs/kelvin) from it. This module dispatches any
accepted input shape to that canonical form using `homeassistant.util.color`.

Brightness is tracked separately by the entity; the normalizer only handles
chromaticity and the chromatic/white distinction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.util import color as color_util

from .const import (
    FIELD_COLOR_NAME,
    FIELD_HEX,
    FIELD_HS,
    FIELD_KELVIN,
    FIELD_RGB,
    FIELD_XY,
    KIND_CHROMATIC,
    KIND_WHITE,
    MAX_KELVIN,
    MIN_KELVIN,
)


@dataclass(frozen=True)
class CanonicalColor:
    """Canonical color: chromaticity + chromatic/white kind + optional kelvin."""

    xy: tuple[float, float]
    kind: str  # KIND_CHROMATIC | KIND_WHITE
    kelvin: int | None = None  # set only when kind == KIND_WHITE


class ColorInputError(ValueError):
    """Raised when a color input is missing/ambiguous/out-of-range."""


def _strip_hex(hex_value: str) -> str:
    h = hex_value.strip().lstrip("#")
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ColorInputError(f"Invalid hex color: {hex_value!r}")
    return h


def _hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    h = _strip_hex(hex_value)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _validate_rgb(rgb: Any) -> tuple[int, int, int]:
    if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
        raise ColorInputError(f"rgb_color must be a 3-element sequence, got {rgb!r}")
    r, g, b = (int(v) for v in rgb)
    if not all(0 <= v <= 255 for v in (r, g, b)):
        raise ColorInputError("rgb_color components must be 0-255")
    return r, g, b


def _validate_hs(hs: Any) -> tuple[float, float]:
    if not isinstance(hs, (list, tuple)) or len(hs) != 2:
        raise ColorInputError(f"hs_color must be a 2-element sequence, got {hs!r}")
    h, s = float(hs[0]), float(hs[1])
    if not 0 <= h <= 360:
        raise ColorInputError("hs_color hue must be 0-360")
    if not 0 <= s <= 100:
        raise ColorInputError("hs_color saturation must be 0-100")
    return h, s


def _validate_xy(xy: Any) -> tuple[float, float]:
    if not isinstance(xy, (list, tuple)) or len(xy) != 2:
        raise ColorInputError(f"xy_color must be a 2-element sequence, got {xy!r}")
    x, y = float(xy[0]), float(xy[1])
    # CIE chromaticities live in [0, 1] but the triangle is much smaller; we
    # don't gamut-clamp here, only sanity-check the storage range.
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        raise ColorInputError("xy_color components must be in [0, 1]")
    return x, y


def _validate_kelvin(kelvin: Any) -> int:
    try:
        k = int(kelvin)
    except (TypeError, ValueError) as err:
        raise ColorInputError(f"color_temp_kelvin must be an int, got {kelvin!r}") from err
    if not MIN_KELVIN <= k <= MAX_KELVIN:
        raise ColorInputError(f"color_temp_kelvin must be in [{MIN_KELVIN}, {MAX_KELVIN}]")
    return k


def normalize(inputs: dict[str, Any]) -> CanonicalColor:
    """Normalize one of the accepted color shapes to canonical form.

    Exactly one shape must be present. Mutual exclusivity is enforced here so
    callers (service handler, config flow) can lean on a single error path.
    """
    keys = {
        FIELD_HEX,
        FIELD_RGB,
        FIELD_HS,
        FIELD_XY,
        FIELD_KELVIN,
        FIELD_COLOR_NAME,
    }
    present = {k: v for k, v in inputs.items() if k in keys and v is not None}
    if not present:
        raise ColorInputError(f"Provide exactly one of: {', '.join(sorted(keys))}")
    if len(present) > 1:
        raise ColorInputError(f"Provide only one color input; got multiple: {sorted(present)}")

    field, value = next(iter(present.items()))

    if field == FIELD_KELVIN:
        kelvin = _validate_kelvin(value)
        # White: store the chromaticity on the Planckian locus so chromatic
        # apply paths still work; remember the kelvin for tunable-white targets.
        r, g, b = color_util.color_temperature_to_rgb(kelvin)
        x, y = color_util.color_RGB_to_xy(int(r), int(g), int(b))
        return CanonicalColor(xy=(x, y), kind=KIND_WHITE, kelvin=kelvin)

    if field == FIELD_HEX:
        r, g, b = _hex_to_rgb(str(value))
    elif field == FIELD_RGB:
        r, g, b = _validate_rgb(value)
    elif field == FIELD_HS:
        h, s = _validate_hs(value)
        r, g, b = color_util.color_hs_to_RGB(h, s)
    elif field == FIELD_XY:
        x, y = _validate_xy(value)
        return CanonicalColor(xy=(x, y), kind=KIND_CHROMATIC)
    elif field == FIELD_COLOR_NAME:
        try:
            r, g, b = color_util.color_name_to_rgb(str(value))
        except ValueError as err:
            raise ColorInputError(f"Unknown color name: {value!r}") from err
    else:  # pragma: no cover - the `keys` set guards this
        raise ColorInputError(f"Unhandled color input: {field}")

    x, y = color_util.color_RGB_to_xy(int(r), int(g), int(b))
    return CanonicalColor(xy=(x, y), kind=KIND_CHROMATIC)


def derive_rgb(canonical: CanonicalColor) -> tuple[int, int, int]:
    """Display-grade sRGB for the swatch/state. Uses kelvin when kind=white."""
    if canonical.kind == KIND_WHITE and canonical.kelvin is not None:
        r, g, b = color_util.color_temperature_to_rgb(canonical.kelvin)
        return int(r), int(g), int(b)
    return color_util.color_xy_to_RGB(*canonical.xy)


def derive_hs(canonical: CanonicalColor) -> tuple[float, float]:
    r, g, b = derive_rgb(canonical)
    return color_util.color_RGB_to_hs(r, g, b)


def derive_kelvin(canonical: CanonicalColor) -> int | None:
    """Return the stored kelvin for kind=white; None for chromatic colors.

    McCamy's approximation will happily return a number for any chromatic xy,
    but for saturated reds/greens/blues that number is meaningless. Emitting
    None makes the data model honest: "this color is a white at K" only holds
    when the user explicitly picked a white.
    """
    if canonical.kind == KIND_WHITE and canonical.kelvin is not None:
        return canonical.kelvin
    return None


def derive_hex(canonical: CanonicalColor) -> str:
    r, g, b = derive_rgb(canonical)
    return "#" + color_util.color_rgb_to_hex(r, g, b).upper()


def compute_source_hex(inputs: dict[str, Any]) -> str | None:
    """Return the literal hex equivalent of the user's input, if one exists.

    For inputs that map cleanly to a single sRGB triple (hex/rgb/hs/
    color_name) we can echo back the exact bytes the user supplied without
    losing them to the xy gamut round-trip. For xy/kelvin inputs there is
    no canonical "source hex" so we return None.

    Callers pass the same dict they'd give to `normalize`; this peeks at
    whichever key is set.
    """
    if FIELD_HEX in inputs and inputs[FIELD_HEX] is not None:
        try:
            r, g, b = _hex_to_rgb(str(inputs[FIELD_HEX]))
        except ColorInputError:
            return None
    elif FIELD_RGB in inputs and inputs[FIELD_RGB] is not None:
        try:
            r, g, b = _validate_rgb(inputs[FIELD_RGB])
        except ColorInputError:
            return None
    elif FIELD_HS in inputs and inputs[FIELD_HS] is not None:
        try:
            h, s = _validate_hs(inputs[FIELD_HS])
        except ColorInputError:
            return None
        r, g, b = color_util.color_hs_to_RGB(h, s)
    elif FIELD_COLOR_NAME in inputs and inputs[FIELD_COLOR_NAME] is not None:
        try:
            r, g, b = color_util.color_name_to_rgb(str(inputs[FIELD_COLOR_NAME]))
        except ValueError:
            return None
    else:
        return None

    return "#" + color_util.color_rgb_to_hex(int(r), int(g), int(b)).upper()
