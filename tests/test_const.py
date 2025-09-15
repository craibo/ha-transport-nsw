"""Test the Transport NSW constants."""

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
    DEFAULT_NAME,
    DEFAULT_STOP_NAME,
    DOMAIN,
    SUBENTRY_TYPE_STOP,
    TRANSPORT_ICONS,
)


class TestConstants:
    """Test the constants module."""

    def test_domain(self):
        """Test domain constant."""
        assert DOMAIN == "transport_nsw"
        assert isinstance(DOMAIN, str)

    def test_config_constants(self):
        """Test configuration constants."""
        assert CONF_STOP_ID == "stop_id"
        assert CONF_ROUTE == "route"
        assert CONF_DESTINATION == "destination"
        
        assert isinstance(CONF_STOP_ID, str)
        assert isinstance(CONF_ROUTE, str)
        assert isinstance(CONF_DESTINATION, str)

    def test_subentry_constants(self):
        """Test subentry constants."""
        assert SUBENTRY_TYPE_STOP == "stop"
        assert isinstance(SUBENTRY_TYPE_STOP, str)

    def test_attribute_constants(self):
        """Test attribute constants."""
        assert ATTR_STOP_ID == "stop_id"
        assert ATTR_ROUTE == "route"
        assert ATTR_DUE_IN == "due"
        assert ATTR_DELAY == "delay"
        assert ATTR_REAL_TIME == "real_time"
        assert ATTR_DESTINATION == "destination"
        
        assert isinstance(ATTR_STOP_ID, str)
        assert isinstance(ATTR_ROUTE, str)
        assert isinstance(ATTR_DUE_IN, str)
        assert isinstance(ATTR_DELAY, str)
        assert isinstance(ATTR_REAL_TIME, str)
        assert isinstance(ATTR_DESTINATION, str)

    def test_default_values(self):
        """Test default value constants."""
        assert DEFAULT_NAME == "Transport NSW"
        assert DEFAULT_STOP_NAME == "Transport NSW Stop"
        
        assert isinstance(DEFAULT_NAME, str)
        assert isinstance(DEFAULT_STOP_NAME, str)

    def test_transport_icons(self):
        """Test transport icons dictionary."""
        assert isinstance(TRANSPORT_ICONS, dict)
        
        # Test all expected keys are present
        expected_modes = [
            "Train",
            "Lightrail", 
            "Bus",
            "Coach",
            "Ferry",
            "Schoolbus",
            "n/a",
            None,
        ]
        
        for mode in expected_modes:
            assert mode in TRANSPORT_ICONS
            assert isinstance(TRANSPORT_ICONS[mode], str)
            assert TRANSPORT_ICONS[mode].startswith("mdi:")

    def test_transport_icons_specific_values(self):
        """Test specific transport icon values."""
        assert TRANSPORT_ICONS["Train"] == "mdi:train"
        assert TRANSPORT_ICONS["Lightrail"] == "mdi:tram"
        assert TRANSPORT_ICONS["Bus"] == "mdi:bus"
        assert TRANSPORT_ICONS["Coach"] == "mdi:bus"
        assert TRANSPORT_ICONS["Ferry"] == "mdi:ferry"
        assert TRANSPORT_ICONS["Schoolbus"] == "mdi:bus"
        assert TRANSPORT_ICONS["n/a"] == "mdi:clock"
        assert TRANSPORT_ICONS[None] == "mdi:clock"

    def test_transport_icons_bus_modes(self):
        """Test bus-related modes use bus icon."""
        bus_modes = ["Bus", "Coach", "Schoolbus"]
        for mode in bus_modes:
            assert TRANSPORT_ICONS[mode] == "mdi:bus"

    def test_transport_icons_fallback(self):
        """Test fallback icon for unknown/empty modes."""
        fallback_modes = ["n/a", None]
        for mode in fallback_modes:
            assert TRANSPORT_ICONS[mode] == "mdi:clock"

    def test_constants_are_strings(self):
        """Test that all string constants are actually strings."""
        string_constants = [
            DOMAIN,
            CONF_STOP_ID,
            CONF_ROUTE,
            CONF_DESTINATION,
            SUBENTRY_TYPE_STOP,
            ATTR_STOP_ID,
            ATTR_ROUTE,
            ATTR_DUE_IN,
            ATTR_DELAY,
            ATTR_REAL_TIME,
            ATTR_DESTINATION,
            DEFAULT_NAME,
            DEFAULT_STOP_NAME,
        ]
        
        for constant in string_constants:
            assert isinstance(constant, str)
            assert len(constant) > 0

    def test_constants_uniqueness(self):
        """Test that constants have unique values where expected."""
        # Config constants should be unique
        config_constants = [CONF_STOP_ID, CONF_ROUTE, CONF_DESTINATION]
        assert len(config_constants) == len(set(config_constants))
        
        # Attribute constants should be unique
        attr_constants = [
            ATTR_STOP_ID,
            ATTR_ROUTE, 
            ATTR_DUE_IN,
            ATTR_DELAY,
            ATTR_REAL_TIME,
            ATTR_DESTINATION,
        ]
        assert len(attr_constants) == len(set(attr_constants))

    def test_icon_format(self):
        """Test that all icons follow MDI format."""
        for mode, icon in TRANSPORT_ICONS.items():
            assert icon.startswith("mdi:")
            assert len(icon) > 4  # More than just "mdi:"
            assert ":" in icon  # Should have the colon separator

    def test_transport_modes_coverage(self):
        """Test that common transport modes are covered."""
        # Common NSW transport modes
        common_modes = ["Train", "Bus", "Ferry", "Lightrail"]
        for mode in common_modes:
            assert mode in TRANSPORT_ICONS

    def test_constants_not_empty(self):
        """Test that constants are not empty strings."""
        non_empty_constants = [
            DOMAIN,
            CONF_STOP_ID,
            CONF_ROUTE,
            CONF_DESTINATION,
            SUBENTRY_TYPE_STOP,
            ATTR_STOP_ID,
            ATTR_ROUTE,
            ATTR_DUE_IN,
            ATTR_DELAY,
            ATTR_REAL_TIME,
            ATTR_DESTINATION,
            DEFAULT_NAME,
            DEFAULT_STOP_NAME,
        ]
        
        for constant in non_empty_constants:
            assert constant.strip() != ""

    def test_attribute_route_consistency(self):
        """Test consistency between config and attribute constants."""
        # These should have the same base name
        assert CONF_STOP_ID == ATTR_STOP_ID
        assert CONF_ROUTE == ATTR_ROUTE
        assert CONF_DESTINATION == ATTR_DESTINATION
