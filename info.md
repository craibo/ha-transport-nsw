# Transport NSW Integration for Home Assistant

Get real-time departure information for NSW public transport directly in Home Assistant.

## What it does

This integration connects to the Transport NSW Open Data API to provide live departure times for:

- 🚌 **Buses** - Sydney Buses, regional coaches, school buses
- 🚆 **Trains** - Sydney Trains, NSW TrainLink services  
- ⛴️ **Ferries** - Sydney Ferries and private operators
- 🚊 **Light Rail** - Inner West and City Metro lines

## Key Features

### 🎯 **Smart Filtering**
- Filter by specific routes (e.g., only T1 trains, Route 380 buses)
- Filter by destination (e.g., only services to Central, Bondi Junction)
- Custom naming for easy identification

### 📊 **Rich Data**
- Real-time departure information
- Delay tracking (early/late services)
- Transport mode detection with appropriate icons
- Comprehensive sensor attributes

### 🏠 **Home Assistant Ready**
- Native sensor entities with proper device classes
- Automatic icon selection based on transport type
- Perfect for dashboard cards and automations
- HACS compatible for easy installation

## Quick Setup

1. **Get API Key**: Register at [Transport NSW Open Data](https://opendata.transport.nsw.gov.au/)
2. **Install**: Add through HACS or manual installation
3. **Configure**: Add your API key in Settings > Integrations
4. **Add Stops**: Configure individual transport stops as needed

## Perfect For

- **Commuters**: Track your daily train/bus times
- **Families**: Monitor school bus arrivals
- **Tourists**: Plan ferry trips and light rail connections
- **Automation**: Create departure alerts and travel notifications

## Example Use Cases

```yaml
# Get notified when your bus is 5 minutes away
automation:
  - alias: "Bus Departure Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.bus_380_to_city
      below: 5
    action:
      - service: notify.phone
        data:
          message: "Bus arriving in {{ states('sensor.bus_380_to_city') }} minutes!"
```

Create travel dashboards, departure boards, and smart home automations based on real NSW transport data.

**Note**: Requires a free Transport NSW Open Data API key. All data comes directly from the official Transport NSW systems.
