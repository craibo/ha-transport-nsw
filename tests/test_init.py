"""Test the Transport NSW integration initialization."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigSubentry
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.transport_nsw import (
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.transport_nsw.const import (
    CONF_DESTINATION,
    CONF_ROUTE,
    CONF_STOP_ID,
    DOMAIN,
    SUBENTRY_TYPE_STOP,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry


class TestAsyncSetupEntry:
    """Test the async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_setup_entry_success(self, hass: HomeAssistant):
        """Test successful setup of config entry."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )

        result = await async_setup_entry(hass, config_entry)

        assert result is True
        assert DOMAIN in hass.data
        assert isinstance(hass.data[DOMAIN], dict)

    @pytest.mark.asyncio
    async def test_setup_entry_with_existing_domain_data(self, hass: HomeAssistant):
        """Test setup when domain data already exists."""
        # Pre-populate domain data
        hass.data[DOMAIN] = {"existing": "data"}
        
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )

        result = await async_setup_entry(hass, config_entry)

        assert result is True
        assert hass.data[DOMAIN] == {"existing": "data"}

    @pytest.mark.asyncio
    async def test_setup_entry_adds_update_listener(self, hass: HomeAssistant):
        """Test that setup adds an update listener."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )

        with patch.object(config_entry, "add_update_listener") as mock_add_listener, \
             patch.object(config_entry, "async_on_unload") as mock_on_unload:
            
            result = await async_setup_entry(hass, config_entry)

        assert result is True
        mock_add_listener.assert_called_once_with(async_reload_entry)
        mock_on_unload.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_entry_forwards_platforms(self, hass: HomeAssistant):
        """Test that setup forwards to sensor platform."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )

        with patch.object(hass.config_entries, "async_forward_entry_setups") as mock_forward:
            result = await async_setup_entry(hass, config_entry)

        assert result is True
        mock_forward.assert_called_once()
        call_args = mock_forward.call_args
        assert call_args[0][0] == config_entry
        assert "sensor" in call_args[0][1]


class TestAsyncUnloadEntry:
    """Test the async_unload_entry function."""

    @pytest.mark.asyncio
    async def test_unload_entry_success(self, hass: HomeAssistant):
        """Test successful unload of config entry."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)
        
        # Setup domain data
        hass.data[DOMAIN] = {config_entry.entry_id: "test_data"}

        with patch.object(hass.config_entries, "async_unload_platforms", return_value=True) as mock_unload:
            result = await async_unload_entry(hass, config_entry)

        assert result is True
        mock_unload.assert_called_once()
        call_args = mock_unload.call_args
        assert call_args[0][0] == config_entry
        assert "sensor" in call_args[0][1]
        
        # Check that entry data was removed
        assert config_entry.entry_id not in hass.data.get(DOMAIN, {})

    @pytest.mark.asyncio
    async def test_unload_entry_failure(self, hass: HomeAssistant):
        """Test unload failure."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)
        
        # Setup domain data
        hass.data[DOMAIN] = {config_entry.entry_id: "test_data"}

        with patch.object(hass.config_entries, "async_unload_platforms", return_value=False) as mock_unload:
            result = await async_unload_entry(hass, config_entry)

        assert result is False
        mock_unload.assert_called_once()
        
        # Check that entry data was NOT removed on failure
        assert config_entry.entry_id in hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_unload_entry_no_domain_data(self, hass: HomeAssistant):
        """Test unload when no domain data exists."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)

        with patch.object(hass.config_entries, "async_unload_platforms", return_value=True) as mock_unload:
            result = await async_unload_entry(hass, config_entry)

        assert result is True
        mock_unload.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_entry_no_entry_data(self, hass: HomeAssistant):
        """Test unload when entry data doesn't exist."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)
        
        # Setup domain data without this entry
        hass.data[DOMAIN] = {"other_entry": "other_data"}

        with patch.object(hass.config_entries, "async_unload_platforms", return_value=True) as mock_unload:
            result = await async_unload_entry(hass, config_entry)

        assert result is True
        mock_unload.assert_called_once()
        
        # Check that other data is preserved
        assert hass.data[DOMAIN] == {"other_entry": "other_data"}


class TestAsyncReloadEntry:
    """Test the async_reload_entry function."""

    @pytest.mark.asyncio
    async def test_reload_entry(self, hass: HomeAssistant):
        """Test config entry reload."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)

        with patch.object(hass.config_entries, "async_reload") as mock_reload:
            await async_reload_entry(hass, config_entry)

        mock_reload.assert_called_once_with(config_entry.entry_id)


class TestIntegrationFlow:
    """Test the complete integration flow."""

    @pytest.mark.asyncio
    async def test_complete_setup_and_unload_flow(self, hass: HomeAssistant):
        """Test complete setup and unload flow."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)

        # Test setup
        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True):
            setup_result = await async_setup_entry(hass, config_entry)

        assert setup_result is True
        assert DOMAIN in hass.data

        # Test unload
        with patch.object(hass.config_entries, "async_unload_platforms", return_value=True):
            unload_result = await async_unload_entry(hass, config_entry)

        assert unload_result is True

    @pytest.mark.asyncio
    async def test_setup_with_subentries(self, hass: HomeAssistant):
        """Test setup with config entry containing subentries."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        
        # Add subentries
        subentry1 = ConfigSubentry(
            data={
                CONF_STOP_ID: "stop_001",
                CONF_NAME: "Central Station",
                CONF_ROUTE: "T1",
                CONF_DESTINATION: "Hornsby",
            },
            subentry_id="subentry_1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Central Station",
            unique_id="entry_stop_001_route_T1_dest_Hornsby",
        )
        
        subentry2 = ConfigSubentry(
            data={
                CONF_STOP_ID: "stop_002",
                CONF_NAME: "Town Hall",
                CONF_ROUTE: "T2",
                CONF_DESTINATION: "Parramatta",
            },
            subentry_id="subentry_2",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Town Hall",
            unique_id="entry_stop_002_route_T2_dest_Parramatta",
        )
        
        config_entry.subentries = {
            "subentry_1": subentry1,
            "subentry_2": subentry2,
        }
        config_entry.add_to_hass(hass)

        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True) as mock_forward:
            result = await async_setup_entry(hass, config_entry)

        assert result is True
        mock_forward.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_legacy_entry(self, hass: HomeAssistant):
        """Test setup with legacy config entry."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "test_api_key",
                CONF_STOP_ID: "test_stop_id",
                CONF_NAME: "Test Stop",
                CONF_ROUTE: "",
                CONF_DESTINATION: "",
            },
        )
        config_entry.add_to_hass(hass)

        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True) as mock_forward:
            result = await async_setup_entry(hass, config_entry)

        assert result is True
        mock_forward.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_entries(self, hass: HomeAssistant):
        """Test setup with multiple config entries."""
        config_entry1 = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key_1"},
            entry_id="entry_1",
        )
        
        config_entry2 = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key_2"},
            entry_id="entry_2",
        )
        
        config_entry1.add_to_hass(hass)
        config_entry2.add_to_hass(hass)

        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True):
            result1 = await async_setup_entry(hass, config_entry1)
            result2 = await async_setup_entry(hass, config_entry2)

        assert result1 is True
        assert result2 is True
        assert DOMAIN in hass.data

    @pytest.mark.asyncio
    async def test_reload_during_config_change(self, hass: HomeAssistant):
        """Test reload functionality during config changes."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "old_api_key"},
        )
        config_entry.add_to_hass(hass)

        # Setup initial entry
        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True):
            await async_setup_entry(hass, config_entry)

        # Simulate config change and reload
        with patch.object(hass.config_entries, "async_reload") as mock_reload:
            await async_reload_entry(hass, config_entry)

        mock_reload.assert_called_once_with(config_entry.entry_id)

    @pytest.mark.asyncio
    async def test_entry_state_transitions(self, hass: HomeAssistant):
        """Test config entry state transitions."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        config_entry.add_to_hass(hass)

        # Initially not loaded
        assert config_entry.state != ConfigEntryState.LOADED

        # Test setup
        with patch.object(hass.config_entries, "async_forward_entry_setups", return_value=True):
            result = await async_setup_entry(hass, config_entry)

        assert result is True

        # Test unload
        with patch.object(hass.config_entries, "async_unload_platforms", return_value=True):
            result = await async_unload_entry(hass, config_entry)

        assert result is True