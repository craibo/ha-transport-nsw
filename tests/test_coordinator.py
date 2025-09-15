"""Test the Transport NSW coordinator."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.transport_nsw.const import (
    ATTR_DELAY,
    ATTR_DESTINATION,
    ATTR_DUE_IN,
    ATTR_REAL_TIME,
    ATTR_ROUTE,
    CONF_DESTINATION,
    CONF_ROUTE,
    CONF_STOP_ID,
    DOMAIN,
    SUBENTRY_TYPE_STOP,
)
from custom_components.transport_nsw.coordinator import (
    TransportNSWCoordinator,
    _get_value,
    _raise_update_failed,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry


class TestCoordinatorHelperFunctions:
    """Test coordinator helper functions."""

    def test_get_value_with_none(self):
        """Test _get_value with None."""
        assert _get_value(None) is None

    def test_get_value_with_na(self):
        """Test _get_value with 'n/a'."""
        assert _get_value("n/a") is None

    def test_get_value_with_valid_value(self):
        """Test _get_value with valid value."""
        assert _get_value("test") == "test"
        assert _get_value(5) == 5
        assert _get_value(True) is True

    def test_raise_update_failed_without_exception(self):
        """Test _raise_update_failed without exception."""
        with pytest.raises(UpdateFailed, match="Test message"):
            _raise_update_failed("Test message")

    def test_raise_update_failed_with_exception(self):
        """Test _raise_update_failed with exception."""
        original_exc = ValueError("Original error")
        with pytest.raises(UpdateFailed, match="Test message") as exc_info:
            _raise_update_failed("Test message", original_exc)
        assert exc_info.value.__cause__ is original_exc


class TestTransportNSWCoordinator:
    """Test TransportNSWCoordinator."""

    @pytest.mark.asyncio
    async def test_init_with_subentry(self, hass: HomeAssistant, mock_config_entry_with_subentries):
        """Test coordinator initialization with subentry."""
        subentry = list(mock_config_entry_with_subentries.subentries.values())[0]
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_with_subentries, subentry)

        assert coordinator.config_entry == mock_config_entry_with_subentries
        assert coordinator.subentry == subentry
        assert coordinator.api_key == "test_api_key"
        assert coordinator.stop_id == "stop_001"
        assert coordinator.route == "T1"
        assert coordinator.destination == "Hornsby"
        assert coordinator.name == "Transport NSW Central Station"

    @pytest.mark.asyncio
    async def test_init_with_legacy_entry(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test coordinator initialization with legacy config entry."""
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)

        assert coordinator.config_entry == mock_config_entry_legacy
        assert coordinator.subentry is None
        assert coordinator.api_key == "test_api_key"
        assert coordinator.stop_id == "test_stop_id"
        assert coordinator.route == ""
        assert coordinator.destination == ""

    @pytest.mark.asyncio
    async def test_init_without_config_entry(self, hass: HomeAssistant):
        """Test coordinator initialization without config entry raises error."""
        with pytest.raises(ValueError, match="Config entry is required"):
            TransportNSWCoordinator(hass, None, None)

    @pytest.mark.asyncio
    async def test_get_coordinator_name_with_subentry(self, hass: HomeAssistant, mock_config_entry_with_subentries):
        """Test coordinator name generation with subentry."""
        subentry = list(mock_config_entry_with_subentries.subentries.values())[0]
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_with_subentries, subentry)
        assert coordinator._get_coordinator_name() == "Central Station"

    @pytest.mark.asyncio
    async def test_get_coordinator_name_with_subentry_no_title(self, hass: HomeAssistant):
        """Test coordinator name generation with subentry without title."""
        entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "test_api_key"})
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123", CONF_NAME: "", CONF_ROUTE: "", CONF_DESTINATION: ""},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="",
            unique_id="entry_123",
        )
        coordinator = TransportNSWCoordinator(hass, entry, subentry)
        assert coordinator._get_coordinator_name() == "Stop 123"

    @pytest.mark.asyncio
    async def test_get_coordinator_name_legacy_with_name(self, hass: HomeAssistant):
        """Test coordinator name generation with legacy entry with name."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key", CONF_STOP_ID: "123", "name": "Custom Name"},
        )
        coordinator = TransportNSWCoordinator(hass, entry, None)
        assert coordinator._get_coordinator_name() == "Custom Name"

    @pytest.mark.asyncio
    async def test_get_coordinator_name_legacy_without_name(self, hass: HomeAssistant):
        """Test coordinator name generation with legacy entry without name."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key", CONF_STOP_ID: "123"},
        )
        coordinator = TransportNSWCoordinator(hass, entry, None)
        assert coordinator._get_coordinator_name() == "Transport NSW"

    @pytest.mark.asyncio
    async def test_update_data_success(self, hass: HomeAssistant, mock_config_entry_legacy, mock_transport_nsw_api, mock_api_response):
        """Test successful data update."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)

        # Configure the hass async_add_executor_job to return the API response
        hass.async_add_executor_job.return_value = mock_api_response

        data = await coordinator._async_update_data()

        assert data[ATTR_ROUTE] == "T1"
        assert data[ATTR_DUE_IN] == 5
        assert data[ATTR_DELAY] == 0
        assert data[ATTR_REAL_TIME] is True
        assert data[ATTR_DESTINATION] == "Hornsby"
        hass.async_add_executor_job.assert_called_once_with(
            mock_transport_nsw_api.get_departures,
            "test_stop_id", "", "", "test_api_key"
        )

    @pytest.mark.asyncio
    async def test_update_data_with_nulls(self, hass: HomeAssistant, mock_config_entry_legacy, mock_transport_nsw_api, mock_api_response_with_nulls):
        """Test data update with None and n/a values."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response_with_nulls
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)

        # Configure the hass async_add_executor_job to return the API response
        hass.async_add_executor_job.return_value = mock_api_response_with_nulls

        data = await coordinator._async_update_data()

        assert data[ATTR_ROUTE] is None
        assert data[ATTR_DUE_IN] is None  # "n/a" should become None
        assert data[ATTR_DELAY] == 0
        assert data[ATTR_REAL_TIME] is True
        assert data[ATTR_DESTINATION] is None

    @pytest.mark.asyncio
    async def test_update_data_none_response(self, hass: HomeAssistant, mock_config_entry_legacy, mock_transport_nsw_api):
        """Test data update with None response from API."""
        mock_transport_nsw_api.get_departures.return_value = None
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)

        # Configure the hass async_add_executor_job to return None
        hass.async_add_executor_job.return_value = None

        with pytest.raises(UpdateFailed, match="No data returned from Transport NSW API"):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_update_data_api_error(self, hass: HomeAssistant, mock_config_entry_legacy, mock_transport_nsw_api):
        """Test data update with API error."""
        mock_transport_nsw_api.get_departures.side_effect = Exception("API Error")
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)

        # Configure the hass async_add_executor_job to raise an exception
        hass.async_add_executor_job.side_effect = Exception("API Error")

        with pytest.raises(UpdateFailed, match="Error communicating with Transport NSW API"):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_update_data_with_subentry_filters(self, hass: HomeAssistant, mock_config_entry_with_subentries, mock_transport_nsw_api, mock_api_response):
        """Test data update with subentry route and destination filters."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response
        subentry = list(mock_config_entry_with_subentries.subentries.values())[0]
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_with_subentries, subentry)

        # Configure the hass async_add_executor_job to return the API response
        hass.async_add_executor_job.return_value = mock_api_response

        await coordinator._async_update_data()

        hass.async_add_executor_job.assert_called_once_with(
            mock_transport_nsw_api.get_departures,
            "stop_001", "T1", "Hornsby", "test_api_key"
        )

    @pytest.mark.asyncio
    async def test_async_update_config(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test configuration update."""
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_legacy, None)
        original_name = coordinator.name

        # Create updated config entry
        updated_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "new_api_key",
                CONF_STOP_ID: "new_stop_id",
                "name": "New Name",
            },
        )

        with patch.object(coordinator, "async_request_refresh") as mock_refresh:
            await coordinator.async_update_config(updated_entry, None)

        assert coordinator.config_entry == updated_entry
        assert coordinator.api_key == "new_api_key"
        assert coordinator.stop_id == "new_stop_id"
        assert coordinator.name == "Transport NSW New Name"
        assert coordinator.name != original_name
        mock_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_config_with_subentry(self, hass: HomeAssistant, mock_config_entry_with_subentries):
        """Test configuration update with subentry."""
        # Start with an existing subentry
        existing_subentry = list(mock_config_entry_with_subentries.subentries.values())[0]
        coordinator = TransportNSWCoordinator(hass, mock_config_entry_with_subentries, existing_subentry)

        # Create new subentry
        new_subentry = ConfigSubentry(
            data={
                CONF_STOP_ID: "new_stop",
                CONF_NAME: "New Stop",
                CONF_ROUTE: "T2",
                CONF_DESTINATION: "Parramatta",
            },
            subentry_id="new_sub",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="New Stop",
            unique_id="entry_new_stop_route_T2_dest_Parramatta",
        )

        with patch.object(coordinator, "async_request_refresh") as mock_refresh:
            await coordinator.async_update_config(mock_config_entry_with_subentries, new_subentry)

        assert coordinator.subentry == new_subentry
        assert coordinator.stop_id == "new_stop"
        assert coordinator.route == "T2"
        assert coordinator.destination == "Parramatta"
        mock_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_configuration_legacy_with_options(self, hass: HomeAssistant):
        """Test loading configuration from legacy entry with options."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key", CONF_STOP_ID: "123"},
            options={CONF_ROUTE: "T2", CONF_DESTINATION: "Parramatta"},
        )
        coordinator = TransportNSWCoordinator(hass, entry, None)

        assert coordinator.route == "T2"
        assert coordinator.destination == "Parramatta"