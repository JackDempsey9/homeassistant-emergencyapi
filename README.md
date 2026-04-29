# EmergencyAPI for Home Assistant

Real-time Australian emergency incident data from all 8 states and territories in your Home Assistant. Bushfires, floods, storms, cyclones, earthquakes, and more.

Powered by [EmergencyAPI](https://emergencyapi.com) -- 27 government feeds, normalised into one API.

## What you get

- **Map pins** for every active incident near your home (geo_location entities)
- **Alert sensor** that turns ON when an emergency is within your configured radius (binary_sensor)
- **Incident count** and **nearest emergency distance** sensors for dashboards
- **All 8 states**: NSW, VIC, QLD, SA, WA, TAS, ACT, NT + national data

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant
2. Search for "EmergencyAPI"
3. Click Install
4. Restart Home Assistant

### Manual

1. Download the latest release from [GitHub Releases](https://github.com/JackDempsey9/homeassistant-emergencyapi/releases)
2. Copy `custom_components/emergencyapi/` to your HA `custom_components/` directory
3. Restart Home Assistant

## Setup

1. Get a **free API key** at [emergencyapi.com/signup](https://emergencyapi.com/signup) (no credit card)
2. In Home Assistant: Settings > Devices & Services > Add Integration > Search "EmergencyAPI"
3. Enter your API key and set your monitoring radius (default: 50 km)

## Entities

| Entity | Type | What it shows |
|--------|------|---------------|
| `geo_location.emergencyapi_*` | Geo Location | Each incident as a pin on the HA map. Shows distance, title, severity. |
| `binary_sensor.emergencyapi_alert` | Binary Sensor | ON when any incident exists within your radius. OFF when clear. |
| `sensor.emergencyapi_incidents` | Sensor | Count of active incidents within your radius. |
| `sensor.emergencyapi_nearest` | Sensor | Distance to the nearest emergency (km). |

## Example automations

### Send a notification when an emergency is nearby

```yaml
automation:
  - alias: "Emergency Alert Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.emergencyapi_alert
        to: "on"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Emergency Alert"
          message: >
            {{ state_attr('sensor.emergencyapi_nearest', 'title') }}
            is {{ states('sensor.emergencyapi_nearest') }} km away.
            Severity: {{ state_attr('sensor.emergencyapi_nearest', 'severity') }}
```

### Turn on a red light during emergencies

```yaml
automation:
  - alias: "Emergency Red Light"
    trigger:
      - platform: state
        entity_id: binary_sensor.emergencyapi_alert
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: binary_sensor.emergencyapi_alert
                state: "on"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.warning_light
                data:
                  color_name: red
                  brightness: 255
          - conditions:
              - condition: state
                entity_id: binary_sensor.emergencyapi_alert
                state: "off"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.warning_light
```

### Voice announcement via Google Home

```yaml
automation:
  - alias: "Emergency Voice Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.emergencyapi_alert
        to: "on"
    condition:
      - condition: state
        entity_id: sensor.emergencyapi_nearest
        attribute: severity
        state: "Extreme"
    action:
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room_speaker
          message: >
            Emergency warning. {{ state_attr('sensor.emergencyapi_nearest', 'title') }}
            is {{ states('sensor.emergencyapi_nearest') }} kilometres away.
```

## FAQ

**How much does it cost?**
Free. EmergencyAPI has a free tier with 500 API calls per day. The integration uses ~288 calls/day at the default 5-minute interval.

**What data sources does this use?**
27 official government feeds including CFS, RFS, CFA, DFES, TFS, QFES, ACT ESA, NT PFES, BOM, Geoscience Australia, and DEA satellite hotspots. Full list at [emergencyapi.com/api/v1/attribution](https://emergencyapi.com/api/v1/attribution).

**How often does it update?**
Every 5 minutes by default. Configurable from 2 to 60 minutes during setup.

**Does it work outside Australia?**
No. EmergencyAPI covers Australian emergencies only.

## Data attribution

Emergency data is sourced from Australian government agencies under various Creative Commons licences. Full attribution details at [emergencyapi.com/attribution](https://emergencyapi.com/attribution).

## Links

- [EmergencyAPI](https://emergencyapi.com)
- [API Documentation](https://emergencyapi.com/docs)
- [Get a free API key](https://emergencyapi.com/signup)
- [Report an issue](https://github.com/JackDempsey9/homeassistant-emergencyapi/issues)
