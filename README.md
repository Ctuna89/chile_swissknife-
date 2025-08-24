# Chile Swissknife Home Assistant Integration

A comprehensive Home Assistant integration for Chilean services, providing real-time information about:

- USD to CLP exchange rate
- UF to CLP value
- Metro de Santiago status
- Red Mobilidad bus stop information
- Latest earthquakes in Chile

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Go to HACS > Integrations
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add `https://github.com/dubov90/chile-swissknife` as a custom repository
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Chile Swissknife" in the integrations list and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract the `chile_swissknife` folder to your `custom_components` directory
3. Restart Home Assistant
4. Go to Settings > Devices & Services > Add Integration
5. Search for "Chile Swissknife" and follow the setup wizard

## Configuration

During setup, you can configure:

- **Bus Stop IDs**: Comma-separated list of bus stop codes (e.g., "PA123, PA456")
- **Update Interval**: How often to update the data (in minutes, between 1-60)

## Services

### show_earthquake_map

Show the latest earthquake on a map.

| Parameter | Description | Example |
|-----------|-------------|---------|
| earthquake_data | Earthquake data to display | `{"latitude": -33.45, "longitude": -70.67, "magnitude": 5.2}` |

**Example service call:**
```yaml
service: chile_swissknife.show_earthquake_map
data:
  earthquake_data:
    latitude: -33.45
    longitude: -70.67
    magnitude: 5.2
Lovelace Card Examples
Currency Cards
yaml
type: entities
title: Chilean Currency Exchange
show_header_toggle: false
entities:
  - entity: sensor.usd_to_clp
    name: USD to CLP
  - entity: sensor.uf_to_clp
    name: UF to CLP
Metro Status Card
yaml
type: glance
title: Metro Status
entities:
  - entity: sensor.metro_de_santiago_status
    name: Metro Status
Bus Stop Card
yaml
type: entities
title: Bus Information
entities:
  - entity: sensor.bus_stop_pa433
    name: Bus Stop PA433
Earthquake Card with Map
yaml
type: map
title: Latest Earthquake
entities:
  - entity: sensor.latest_earthquake
    name: Latest Earthquake
Supported APIs
Currency Exchange: mindicador.cl

Metro Status: metro.cl

Bus Information: api.xor.cl

Earthquakes: api.gael.cl

Support
If you encounter any issues or have questions:

Check the GitHub Issues page

Create a new issue if your problem hasn't been reported

Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
