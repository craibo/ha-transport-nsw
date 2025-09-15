"""Test the Transport NSW sensor."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_API_KEY, CONF_NAME, ATTR_MODE
from homeassistant.core import HomeAssistant

from custom_components.transport_nsw.const import (
    ATTR_DELAY,
    ATTR_DESTINATION,
    ATTR_DUE_IN,
    ATTR_REAL_TIME,
    ATTR_ROUTE,
    ATTR_STOP_ID,
    CONF_DESTINATION,
    CONF_ROUTE,
    CONF_STOP_ID,
    DOMAIN,
    SUBENTRY_TYPE_STOP,
    TRANSPORT_ICONS,
)
from custom_components.transport_nsw.coordinator import TransportNSWCoordinator
from custom_components.transport_nsw.sensor import (
    TransportNSWSensor,
    async_setup_entry,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry


class TestAsyncSetupEntry:
    """Test the async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_setup_entry_legacy(self, hass: HomeAssistant, mock_transport_nsw_api, mock_api_response):
        """Test setup with legacy config entry."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response
        mock_add_entities = Mock()
        
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "test_api_key",
                CONF_STOP_ID: "test_stop_id",
                CONF_NAME: "Test Stop",
            },
        )

        await async_setup_entry(hass, config_entry, mock_add_entities)

        mock_add_entities.assert_called_once()
        entities = mock_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert isinstance(entities[0], TransportNSWSensor)

    @pytest.mark.asyncio
    async def test_setup_entry_with_subentries(self, hass: HomeAssistant, mock_transport_nsw_api, mock_api_response):
        """Test setup with config entry containing subentries."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response
        mock_add_entities = Mock()
        
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
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
            unique_id="unique_test",
        )
        config_entry.subentries = {"subentry_1": subentry}

        await async_setup_entry(hass, config_entry, mock_add_entities)

        mock_add_entities.assert_called_once()
        entities = mock_add_entities.call_args[0][0]
        assert len(entities) == 1
        assert isinstance(entities[0], TransportNSWSensor)

    @pytest.mark.asyncio
    async def test_setup_entry_with_multiple_subentries(self, hass: HomeAssistant, mock_transport_nsw_api, mock_api_response):
        """Test setup with multiple subentries."""
        mock_transport_nsw_api.get_departures.return_value = mock_api_response
        mock_add_entities = Mock()
        
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )
        
        subentry1 = ConfigSubentry(
            data={CONF_STOP_ID: "stop_001", CONF_NAME: "Stop 1"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Stop 1",
            unique_id="unique_test",
        )
        subentry2 = ConfigSubentry(
            data={CONF_STOP_ID: "stop_002", CONF_NAME: "Stop 2"},
            subentry_id="sub2",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Stop 2",
            unique_id="unique_test",
        )
        config_entry.subentries = {"sub1": subentry1, "sub2": subentry2}

        await async_setup_entry(hass, config_entry, mock_add_entities)

        mock_add_entities.assert_called_once()
        entities = mock_add_entities.call_args[0][0]
        assert len(entities) == 2

    @pytest.mark.asyncio
    async def test_setup_entry_no_subentries(self, hass: HomeAssistant):
        """Test setup with config entry containing no subentries."""
        mock_add_entities = Mock()
        
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test_api_key"},
        )

        await async_setup_entry(hass, config_entry, mock_add_entities)

        mock_add_entities.assert_called_once()
        entities = mock_add_entities.call_args[0][0]
        assert len(entities) == 0


class TestTransportNSWSensor:
    """Test the TransportNSWSensor class."""

    @pytest.mark.asyncio
    async def test_init_legacy_mode(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test sensor initialization in legacy mode."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.coordinator == coordinator
        assert sensor.config_entry == mock_config_entry_legacy
        assert sensor.subentry is None
        assert sensor.unique_id == f"{DOMAIN}_{mock_config_entry_legacy.entry_id}"

    @pytest.mark.asyncio
    async def test_init_subentry_mode(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor initialization with subentry."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={
                CONF_STOP_ID: "123",
                CONF_ROUTE: "T1",
                CONF_DESTINATION: "Hornsby",
            },
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Test Stop",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)

        assert sensor.subentry == subentry
        expected_unique_id = f"{DOMAIN}_{mock_config_entry_modern.entry_id}_123_route_T1_dest_Hornsby"
        assert sensor.unique_id == expected_unique_id

    @pytest.mark.asyncio
    async def test_init_subentry_no_route_or_destination(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor initialization with subentry without route or destination."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Test Stop",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)

        expected_unique_id = f"{DOMAIN}_{mock_config_entry_modern.entry_id}_123"
        assert sensor.unique_id == expected_unique_id

    @pytest.mark.asyncio
    async def test_name_legacy_mode(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test sensor name in legacy mode."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.name == "Test Stop"

    @pytest.mark.asyncio
    async def test_name_legacy_mode_no_name(self, hass: HomeAssistant):
        """Test sensor name in legacy mode without name."""
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "test", CONF_STOP_ID: "123"},
        )
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, config_entry, None)

        assert sensor.name == "Transport NSW Stop"

    @pytest.mark.asyncio
    async def test_name_subentry_with_custom_name(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor name with subentry custom name."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123", CONF_NAME: "My Custom Stop"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Default Title",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        assert sensor.name == "My Custom Stop"

    @pytest.mark.asyncio
    async def test_name_subentry_with_title(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor name with subentry title."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Subentry Title",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        assert sensor.name == "Subentry Title"

    @pytest.mark.asyncio
    async def test_name_subentry_generated(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor name generation from subentry data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={
                CONF_STOP_ID: "123",
                CONF_ROUTE: "T1",
                CONF_DESTINATION: "Hornsby",
            },
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        assert sensor.name == "Stop 123 Route T1 to Hornsby"

    @pytest.mark.asyncio
    async def test_name_subentry_generated_route_only(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor name generation with route only."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123", CONF_ROUTE: "T1"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        assert sensor.name == "Stop 123 Route T1"

    @pytest.mark.asyncio
    async def test_name_subentry_generated_destination_only(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test sensor name generation with destination only."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123", CONF_DESTINATION: "Hornsby"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        assert sensor.name == "Stop 123 to Hornsby"

    @pytest.mark.asyncio
    async def test_native_value_with_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test native value with coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = {ATTR_DUE_IN: 5}
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.native_value == 5

    @pytest.mark.asyncio
    async def test_native_value_no_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test native value with no coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = None
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.native_value is None

    @pytest.mark.asyncio
    async def test_extra_state_attributes_with_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test extra state attributes with coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = {
            ATTR_ROUTE: "T1",
            ATTR_DELAY: 2,
            ATTR_REAL_TIME: True,
            ATTR_DESTINATION: "Hornsby",
            ATTR_MODE: "Train",
        }
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        attributes = sensor.extra_state_attributes

        expected = {
            ATTR_STOP_ID: "test_stop_id",
            ATTR_ROUTE: "T1",
            ATTR_DELAY: 2,
            ATTR_REAL_TIME: True,
            ATTR_DESTINATION: "Hornsby",
            ATTR_MODE: "Train",
        }
        assert attributes == expected

    @pytest.mark.asyncio
    async def test_extra_state_attributes_subentry(self, hass: HomeAssistant, mock_config_entry_modern):
        """Test extra state attributes with subentry."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = {ATTR_ROUTE: "T1"}
        subentry = ConfigSubentry(
            data={CONF_STOP_ID: "123"},
            subentry_id="sub1",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="Test Stop",
            unique_id="unique_test",
        )
        
        sensor = TransportNSWSensor(coordinator, mock_config_entry_modern, subentry)
        attributes = sensor.extra_state_attributes

        assert attributes[ATTR_STOP_ID] == "123"

    @pytest.mark.asyncio
    async def test_extra_state_attributes_no_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test extra state attributes with no coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = None
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.extra_state_attributes is None

    @pytest.mark.asyncio
    async def test_icon_with_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test icon with coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = {ATTR_MODE: "Train"}
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.icon == TRANSPORT_ICONS["Train"]

    @pytest.mark.asyncio
    async def test_icon_unknown_mode(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test icon with unknown transport mode."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = {ATTR_MODE: "Unknown"}
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.icon == TRANSPORT_ICONS[None]

    @pytest.mark.asyncio
    async def test_icon_no_data(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test icon with no coordinator data."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.data = None
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.icon == TRANSPORT_ICONS[None]

    @pytest.mark.asyncio
    async def test_icon_all_modes(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test icon for all transport modes."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        for mode, expected_icon in TRANSPORT_ICONS.items():
            coordinator.data = {ATTR_MODE: mode}
            assert sensor.icon == expected_icon

    @pytest.mark.asyncio
    async def test_async_update_config(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test async_update_config method."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        coordinator.async_update_config = AsyncMock()
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        new_config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_API_KEY: "new_key", CONF_STOP_ID: "new_stop"},
        )
        new_subentry = ConfigSubentry(
            data={CONF_STOP_ID: "new_stop"},
            subentry_id="new_sub",
            subentry_type=SUBENTRY_TYPE_STOP,
            title="New Stop",
            unique_id="unique_test",
        )

        with patch.object(sensor, "async_write_ha_state") as mock_write_state:
            await sensor.async_update_config(new_config_entry, new_subentry)

        assert sensor.config_entry == new_config_entry
        assert sensor.subentry == new_subentry
        coordinator.async_update_config.assert_called_once_with(new_config_entry, new_subentry)
        mock_write_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_config_no_coordinator_method(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test async_update_config when coordinator doesn't have the method."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        # Don't add async_update_config method to coordinator
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        new_config_entry = MockConfigEntry(domain=DOMAIN, data={CONF_API_KEY: "new_key"})

        with patch.object(sensor, "async_write_ha_state") as mock_write_state:
            await sensor.async_update_config(new_config_entry, None)

        assert sensor.config_entry == new_config_entry
        mock_write_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_device_info(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test device info is set correctly."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        device_info = sensor.device_info
        assert device_info["identifiers"] == {(DOMAIN, mock_config_entry_legacy.entry_id)}
        assert device_info["name"] == "Transport NSW"
        assert device_info["manufacturer"] == "Transport NSW"

    @pytest.mark.asyncio
    async def test_sensor_attributes(self, hass: HomeAssistant, mock_config_entry_legacy):
        """Test sensor class attributes."""
        coordinator = Mock(spec=TransportNSWCoordinator)
        sensor = TransportNSWSensor(coordinator, mock_config_entry_legacy, None)

        assert sensor.attribution == "Data provided by Transport NSW"
        assert sensor.device_class is not None
        assert sensor.state_class is not None
        assert sensor.native_unit_of_measurement is not None