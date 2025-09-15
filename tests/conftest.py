"""Common fixtures for the Transport NSW tests."""

from unittest.mock import patch

import pytest

# Use the homeassistant custom component plugin but add our own fixture
# pytest_plugins = "pytest_homeassistant_custom_component"

from homeassistant.core import HomeAssistant


@pytest.fixture
def hass():
    """Create a test HomeAssistant instance."""
    from unittest.mock import Mock, AsyncMock
    
    # Create a mock HomeAssistant instance with the methods we need
    hass_instance = Mock()
    hass_instance.data = {}
    hass_instance.config_entries = AsyncMock()
    hass_instance.async_add_executor_job = AsyncMock()
    
    return hass_instance

from custom_components.transport_nsw.const import (
    CONF_DESTINATION,
    CONF_ROUTE,
    CONF_STOP_ID,
    DOMAIN,
    SUBENTRY_TYPE_STOP,
)
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_API_KEY, CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def mock_transport_nsw_api():
    """Mock the TransportNSW API."""
    with patch("custom_components.transport_nsw.coordinator.TransportNSW") as mock_class:
        mock_instance = mock_class.return_value
        yield mock_instance


@pytest.fixture
def mock_transport_nsw_config_flow():
    """Mock the TransportNSW API for config flow."""
    with patch("custom_components.transport_nsw.config_flow.TransportNSW") as mock_class:
        mock_instance = mock_class.return_value
        yield mock_instance


@pytest.fixture
def mock_config_entry_legacy():
    """Mock legacy config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_api_key",
            CONF_STOP_ID: "test_stop_id",
            CONF_NAME: "Test Stop",
            CONF_ROUTE: "",
            CONF_DESTINATION: "",
        },
        unique_id="test_stop_id",
        title="Test Stop",
    )


@pytest.fixture
def mock_config_entry_modern():
    """Mock modern config entry without stop_id in data."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_api_key",
            CONF_NAME: "Transport NSW",
        },
        title="Transport NSW",
    )


@pytest.fixture
def mock_config_entry_with_subentries():
    """Mock config entry with subentries."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY: "test_api_key"},
        title="Transport NSW",
    )

    subentry = ConfigSubentry(
        data={
            CONF_STOP_ID: "stop_001",
            CONF_NAME: "Central Station",
            CONF_ROUTE: "T1",
            CONF_DESTINATION: "Hornsby",
        },
        subentry_id="subentry_1",
        subentry_type=SUBENTRY_TYPE_STOP,
        title="Central Station",
        unique_id="test_entry_stop_001_route_T1_dest_Hornsby",
    )

    entry.subentries = {"subentry_1": subentry}
    return entry


@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    return {
        "route": "T1",
        "due": 5,
        "delay": 0,
        "real_time": True,
        "destination": "Hornsby",
        "mode": "Train",
    }


@pytest.fixture
def mock_api_response_with_nulls():
    """Mock API response with None and n/a values."""
    return {
        "route": None,
        "due": "n/a",
        "delay": 0,
        "real_time": True,
        "destination": None,
        "mode": "Bus",
    }


@pytest.fixture
def mock_api_response_none():
    """Mock API returning None."""
    return None
