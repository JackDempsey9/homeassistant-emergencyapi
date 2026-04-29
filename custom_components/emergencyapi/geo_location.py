import logging

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_EVENT_TYPE, ATTR_SEVERITY, ATTR_SOURCE_AGENCY, ATTR_SOURCE_STATE, ATTR_STATUS, ATTR_WARNING_LEVEL, DOMAIN
from .coordinator import EmergencyAPICoordinator

_LOGGER = logging.getLogger(__name__)

SOURCE = "emergencyapi"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EmergencyAPICoordinator = hass.data[DOMAIN][entry.entry_id]
    known_ids: set[str] = set()

    @callback
    def _async_update() -> None:
        new_entities = []
        current_ids = set()

        for feature in coordinator.incidents:
            incident_id = feature.get("id", "")
            current_ids.add(incident_id)

            if incident_id not in known_ids:
                known_ids.add(incident_id)
                new_entities.append(
                    EmergencyAPIGeoLocation(coordinator, feature, incident_id)
                )

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_update)
    _async_update()


class EmergencyAPIGeoLocation(CoordinatorEntity, GeolocationEvent):

    _attr_source = SOURCE

    def __init__(
        self,
        coordinator: EmergencyAPICoordinator,
        feature: dict,
        incident_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._incident_id = incident_id
        self._attr_unique_id = f"{DOMAIN}_{incident_id}"

    @property
    def _feature(self) -> dict | None:
        for f in self.coordinator.incidents:
            if f.get("id") == self._incident_id:
                return f
        return None

    @property
    def available(self) -> bool:
        return self._feature is not None

    @property
    def name(self) -> str:
        feature = self._feature
        if feature is None:
            return self._incident_id
        props = feature.get("properties", {})
        return props.get("title", self._incident_id)

    @property
    def latitude(self) -> float | None:
        feature = self._feature
        if feature is None:
            return None
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) >= 2:
            return coords[1]
        return None

    @property
    def longitude(self) -> float | None:
        feature = self._feature
        if feature is None:
            return None
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) >= 2:
            return coords[0]
        return None

    @property
    def distance(self) -> float | None:
        feature = self._feature
        if feature is None:
            return None
        props = feature.get("properties", {})
        return props.get("distance")

    @property
    def extra_state_attributes(self) -> dict:
        feature = self._feature
        if feature is None:
            return {}
        props = feature.get("properties", {})
        source = props.get("source", {})
        return {
            ATTR_EVENT_TYPE: props.get("eventType"),
            ATTR_SEVERITY: props.get("severity"),
            ATTR_WARNING_LEVEL: props.get("warningLevel"),
            ATTR_STATUS: props.get("status"),
            ATTR_SOURCE_STATE: source.get("state"),
            ATTR_SOURCE_AGENCY: source.get("agency"),
        }
