# Transport NSW for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

_Integration to retrieve real-time transport departure information from Transport NSW._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show real-time departure information for NSW transport stops.

## Features

- **Real-time departures**: Get live departure times for buses, trains, ferries, and light rail
- **Multiple stops**: Monitor multiple transport stops with a single API key
- **Route filtering**: Filter departures by specific routes (e.g., T1, T4, M20)
- **Destination filtering**: Filter departures by destination
- **Custom naming**: Assign custom names to your transport sensors
- **Legacy support**: Maintains compatibility with existing configurations

## Installation

### HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. In HACS, go to "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL: `https://github.com/craibo/ha-transport-nsw`
5. Select "Integration" as the category
6. Click "Add"
7. Find "Transport NSW" in the integration list and click "Install"
8. Restart Home Assistant

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
2. If you do not have a `custom_components` directory (folder) there, you need to create it
3. In the `custom_components` directory (folder) create a new folder called `transport_nsw`
4. Download _all_ the files from the `custom_components/transport_nsw/` directory (folder) in this repository
5. Place the files you downloaded in the new directory (folder) you created
6. Restart Home Assistant

## Configuration

### Get Your API Key

1. Go to [Transport NSW Open Data](https://opendata.transport.nsw.gov.au/)
2. Register for a free account
3. Create a new application
4. Add the "Trip Planner APIs" to your application
5. Your API key will be displayed in your application details

### Setup Integration

1. In Home Assistant, go to **Configuration** > **Integrations**
2. Click the **+ Add Integration** button
3. Search for "Transport NSW"
4. Enter your API key and optionally a custom name
5. Click **Submit**

### Add Transport Stops

After setting up the main integration:

1. Go to **Configuration** > **Integrations**
2. Find your "Transport NSW" integration
3. Click **Configure** > **Add Entry** > **Transport stop**
4. Enter the stop details:
   - **Stop ID**: The Transport NSW stop ID (required)
   - **Name**: Custom name for this stop (optional)
   - **Route**: Filter by specific route (optional, e.g., "T1", "M20")
   - **Destination**: Filter by destination (optional, e.g., "Central", "Bondi Junction")

### Finding Stop IDs

You can find stop IDs using several methods:

1. **TripView App**: Look for the stop ID in the app details
2. **Transport NSW Website**: Check the URL when viewing a stop
3. **Google Transit**: The stop ID is often in the URL
4. **Physical stops**: Some stops display their ID on signage

Common Sydney stop IDs:
- Central Station: `10101100`
- Circular Quay: `10101120`
- Town Hall: `10101124`
- Wynyard: `10101123`

## Configuration Examples

### Basic Setup

A simple setup with just an API key:

```yaml
# This creates the main integration entry
# Individual stops are added through the UI
```

### Multiple Stops with Filtering

Examples of different stop configurations:

- **Central Station - All services**: Stop ID `10101100`
- **Central Station - T1 line only**: Stop ID `10101100`, Route `T1`
- **Central Station - T1 to Hornsby**: Stop ID `10101100`, Route `T1`, Destination `Hornsby`
- **Bus stop - Route 380 only**: Stop ID `209234`, Route `380`

## Sensor Attributes

Each transport sensor provides the following attributes:

Attribute | Description
-- | --
`stop_id` | The Transport NSW stop ID
`route` | The route number/name (e.g., "T1", "380")
`destination` | The destination of the service
`due` | Minutes until departure (also the sensor state)
`delay` | Delay in minutes (positive = late, negative = early)
`real_time` | Whether the data is real-time (true/false)
`mode` | Transport mode (Train, Bus, Ferry, Lightrail, etc.)

## Sensor States and Icons

- **State**: Minutes until departure (numeric value)
- **Icon**: Automatically selected based on transport mode:
  - `mdi:train` for trains
  - `mdi:bus` for buses and coaches
  - `mdi:ferry` for ferries
  - `mdi:tram` for light rail
  - `mdi:clock` for unknown or unavailable

## Automations

### Example: Departure Notification

```yaml
automation:
  - alias: "Bus Departure Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.bus_stop_380_to_circular_quay
      below: 5
    condition:
      - condition: state
        entity_id: person.your_name
        state: 'home'
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "Bus 380 departing in {{ states('sensor.bus_stop_380_to_circular_quay') }} minutes!"
```

### Example: Travel Dashboard

```yaml
# In your Lovelace dashboard
type: entities
title: My Commute
entities:
  - sensor.central_station_t1_to_hornsby
  - sensor.bus_stop_380_to_circular_quay
  - sensor.ferry_wharf_to_manly
```

## Troubleshooting

### Common Issues

**"Cannot connect to Transport NSW API"**
- Check your API key is correct
- Ensure you've added "Trip Planner APIs" to your application
- Verify the stop ID exists

**"No data returned from API"**
- The stop ID might be incorrect
- The stop might not have any upcoming departures
- Try a different stop ID to test

**"Sensor shows 'unknown'"**
- The API might be temporarily unavailable
- Check if the transport service is running (late nights, public holidays)

### Enable Debug Logging

Add this to your `configuration.yaml` to enable detailed logging:

```yaml
logger:
  default: info
  logs:
    custom_components.transport_nsw: debug
    TransportNSW: debug
```

### API Limits

- The free Transport NSW API has rate limits
- If you have many sensors, departures are fetched every 60 seconds by default
- Contact Transport NSW if you need higher limits

## Development

### Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Run linting:
   ```bash
   ruff check .
   black .
   ```

### Project Structure

```
custom_components/transport_nsw/
├── __init__.py          # Integration entry point
├── config_flow.py       # Configuration flow
├── const.py            # Constants
├── coordinator.py      # Data update coordinator
├── manifest.json       # Integration metadata
├── sensor.py           # Sensor platform
└── strings.json        # UI strings
```

### Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components.transport_nsw

# Run specific test file
pytest tests/test_sensor.py
```

## Contributing

If you want to contribute to this project, please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

- 🐛 **Bug reports**: [Open an issue](https://github.com/craibo/ha-transport-nsw/issues)
- 💡 **Feature requests**: [Open an issue](https://github.com/craibo/ha-transport-nsw/issues)
- ❓ **Questions**: [GitHub Discussions](https://github.com/craibo/ha-transport-nsw/discussions)

---

***

[transport_nsw]: https://github.com/craibo/ha-transport-nsw
[buymecoffee]: https://www.buymeacoffee.com/craibo
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/craibo/ha-transport-nsw.svg?style=for-the-badge
[commits]: https://github.com/craibo/ha-transport-nsw/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/craibo/ha-transport-nsw.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40craibo-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/craibo/ha-transport-nsw.svg?style=for-the-badge
[releases]: https://github.com/craibo/ha-transport-nsw/releases
