"""Unit tests for the color normalizer.

These are pure-Python tests (no HA event loop) so they're cheap to run and
catch the bulk of normalization regressions before any integration tests.
"""

from __future__ import annotations

import pytest

from custom_components.color.color_math import (
    ColorInputError,
    derive_hex,
    derive_hs,
    derive_kelvin,
    derive_rgb,
    normalize,
)
from custom_components.color.const import (
    FIELD_COLOR_NAME,
    FIELD_HEX,
    FIELD_HS,
    FIELD_KELVIN,
    FIELD_RGB,
    FIELD_XY,
    KIND_CHROMATIC,
    KIND_WHITE,
)


def test_normalize_requires_exactly_one_shape() -> None:
    with pytest.raises(ColorInputError):
        normalize({})
    with pytest.raises(ColorInputError):
        normalize({FIELD_HEX: "#FF0000", FIELD_RGB: [0, 255, 0]})


@pytest.mark.parametrize(
    ("hex_in", "expected_rgb"),
    [
        ("#FF0000", (255, 0, 0)),
        ("ff0000", (255, 0, 0)),  # no leading '#'
        ("#00ff00", (0, 255, 0)),
        ("#0000FF", (0, 0, 255)),
    ],
)
def test_normalize_hex_round_trips_via_xy(hex_in: str, expected_rgb: tuple[int, int, int]) -> None:
    canonical = normalize({FIELD_HEX: hex_in})
    assert canonical.kind == KIND_CHROMATIC
    # xy -> rgb may differ slightly from input due to gamma curve, but the
    # display-derived rgb should be within a few units.
    r, g, b = derive_rgb(canonical)
    # xy is chromaticity only; round-trip through Wide-RGB D65 introduces a
    # small per-channel drift (more pronounced at the gamut edges, e.g. pure
    # primaries). The dominant channel should clearly win; non-dominant
    # channels should stay near zero.
    dominant = expected_rgb.index(max(expected_rgb))
    for i, got in enumerate((r, g, b)):
        if i == dominant:
            assert got > 200, f"dominant channel too low: {got}"
        else:
            assert got < 30, f"off-channel too high: {got}"


def test_normalize_invalid_hex() -> None:
    with pytest.raises(ColorInputError):
        normalize({FIELD_HEX: "#GGGGGG"})
    with pytest.raises(ColorInputError):
        normalize({FIELD_HEX: "#FFF"})  # short hex not accepted


def test_normalize_rgb_validates_range() -> None:
    with pytest.raises(ColorInputError):
        normalize({FIELD_RGB: [256, 0, 0]})
    with pytest.raises(ColorInputError):
        normalize({FIELD_RGB: [0, 0]})  # too few components
    canonical = normalize({FIELD_RGB: [128, 64, 32]})
    assert canonical.kind == KIND_CHROMATIC


def test_normalize_hs_validates_range() -> None:
    with pytest.raises(ColorInputError):
        normalize({FIELD_HS: [400, 50]})  # hue out of range
    with pytest.raises(ColorInputError):
        normalize({FIELD_HS: [180, 150]})  # saturation > 100
    canonical = normalize({FIELD_HS: [180, 50]})
    assert canonical.kind == KIND_CHROMATIC


def test_normalize_xy_passthrough() -> None:
    canonical = normalize({FIELD_XY: [0.4, 0.4]})
    assert canonical.kind == KIND_CHROMATIC
    assert canonical.xy == (0.4, 0.4)


def test_normalize_kelvin_sets_kind_white() -> None:
    canonical = normalize({FIELD_KELVIN: 4000})
    assert canonical.kind == KIND_WHITE
    assert canonical.kelvin == 4000
    # The xy on the Planckian locus should be in the warm-white quadrant.
    x, y = canonical.xy
    assert 0.25 < x < 0.45
    assert 0.25 < y < 0.45


def test_normalize_kelvin_out_of_range() -> None:
    with pytest.raises(ColorInputError):
        normalize({FIELD_KELVIN: 500})
    with pytest.raises(ColorInputError):
        normalize({FIELD_KELVIN: 100_000})


def test_normalize_color_name() -> None:
    canonical = normalize({FIELD_COLOR_NAME: "red"})
    assert canonical.kind == KIND_CHROMATIC
    r, _g, _b = derive_rgb(canonical)
    assert r > 200


def test_normalize_unknown_color_name() -> None:
    with pytest.raises(ColorInputError):
        normalize({FIELD_COLOR_NAME: "definitely-not-a-color"})


def test_derive_hex_format() -> None:
    canonical = normalize({FIELD_HEX: "#FF8000"})
    hex_out = derive_hex(canonical)
    assert hex_out.startswith("#")
    assert len(hex_out) == 7
    assert hex_out == hex_out.upper()


def test_derive_kelvin_for_white_returns_stored_value() -> None:
    canonical = normalize({FIELD_KELVIN: 3500})
    assert derive_kelvin(canonical) == 3500


def test_derive_kelvin_for_chromatic_returns_none() -> None:
    """Chromatic colors must not emit a McCamy-guessed kelvin."""
    canonical = normalize({FIELD_HEX: "#FF0000"})
    assert derive_kelvin(canonical) is None


def test_derive_hs_in_expected_ranges() -> None:
    canonical = normalize({FIELD_HEX: "#FF0000"})
    h, s = derive_hs(canonical)
    assert 0 <= h <= 360
    assert 0 <= s <= 100
