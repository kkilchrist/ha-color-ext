"""Shared pytest fixtures for the Color helper."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(request: pytest.FixtureRequest) -> None:
    """Enable loading of custom_components/ only for HA-dependent tests.

    Activates the pytest-homeassistant-custom-component fixture lazily so that
    pure-Python unit tests (e.g. color_math) don't get pulled into the async
    HA fixture graph.
    """
    if "hass" in request.fixturenames:
        request.getfixturevalue("enable_custom_integrations")
