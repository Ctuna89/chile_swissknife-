"""Sensor platform for Chile Swissknife."""
import asyncio
import logging
from datetime import timedelta
import aiohttp
import xmltodict
import json

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Chile Swissknife sensor based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        USDClpSensor(coordinator),
        UFClpSensor(coordinator),
        MetroStatusSensor(coordinator),
        EarthquakeSensor(coordinator),
    ]
    
    # Add bus stop sensors if configured
    bus_stops = entry.data.get("bus_stops", [])
    for stop in bus_stops:
        sensors.append(BusStopSensor(coordinator, stop))
    
    async_add_entities(sensors, False)


class ChileSwissknifeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Chile Swissknife sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()


class USDClpSensor(ChileSwissknifeSensor):
    """Representation of a USD to CLP sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = "USD to CLP"
        self._unit = "CLP"
        self._icon = "mdi:currency-usd"
        self._unique_id = "usd_to_clp"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
        
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        # Get data from coordinator
        usd_data = await self._fetch_usd_data()
        self._state = usd_data.get("value")
        
    async def _fetch_usd_data(self):
        """Fetch USD to CLP data."""
        url = "https://mindicador.cl/api/dolar"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return {
                        "value": data.get("serie", [{}])[0].get("valor"),
                        "date": data.get("serie", [{}])[0].get("fecha")
                    }
        except Exception as e:
            _LOGGER.error("Error fetching USD data: %s", e)
            return {"value": None, "date": None}


class UFClpSensor(ChileSwissknifeSensor):
    """Representation of a UF to CLP sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = "UF to CLP"
        self._unit = "CLP"
        self._icon = "mdi:cash"
        self._unique_id = "uf_to_clp"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
        
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        # Get data from coordinator
        uf_data = await self._fetch_uf_data()
        self._state = uf_data.get("value")
        
    async def _fetch_uf_data(self):
        """Fetch UF to CLP data."""
        url = "https://mindicador.cl/api/uf"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return {
                        "value": data.get("serie", [{}])[0].get("valor"),
                        "date": data.get("serie", [{}])[0].get("fecha")
                    }
        except Exception as e:
            _LOGGER.error("Error fetching UF data: %s", e)
            return {"value": None, "date": None}


class MetroStatusSensor(ChileSwissknifeSensor):
    """Representation of a Metro de Santiago status sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = "Metro de Santiago Status"
        self._icon = "mdi:subway"
        self._state = "Operational"
        self._attributes = {}
        self._unique_id = "metro_status"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id
        
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        metro_data = await self._fetch_metro_status()
        self._state = metro_data.get("status", "Unknown")
        self._attributes = metro_data.get("lines", {})
        
    async def _fetch_metro_status(self):
        """Fetch Metro de Santiago status."""
        url = "https://www.metro.cl/api/estado-red"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    status = "Operational"
                    lines = {}
                    
                    for line in data.get("lines", []):
                        lines[line.get("name")] = line.get("status")
                        if line.get("status") != "Operativa":
                            status = "Issues"
                    
                    return {"status": status, "lines": lines}
        except Exception as e:
            _LOGGER.error("Error fetching Metro status: %s", e)
            return {"status": "Unknown", "lines": {}}


class BusStopSensor(ChileSwissknifeSensor):
    """Representation of a bus stop sensor."""
    
    def __init__(self, coordinator, stop_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.stop_id = stop_id
        self._name = f"Bus Stop {stop_id}"
        self._icon = "mdi:bus"
        self._state = None
        self._attributes = {}
        self._unique_id = f"bus_stop_{stop_id}"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id
        
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        bus_data = await self._fetch_bus_data(self.stop_id)
        self._state = len(bus_data.get("buses", []))
        self._attributes = bus_data
        
    async def _fetch_bus_data(self, stop_id):
        """Fetch bus data for a specific stop."""
        url = f"https://api.xor.cl/red/bus-stop/{stop_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            _LOGGER.error("Error fetching bus data for stop %s: %s", stop_id, e)
            return {"buses": [], "stop_id": stop_id, "error": str(e)}


class EarthquakeSensor(ChileSwissknifeSensor):
    """Representation of an earthquake sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = "Latest Earthquake"
        self._icon = "mdi:earthquake"
        self._state = None
        self._attributes = {}
        self._unique_id = "latest_earthquake"
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id
        
    @property
    def icon(self):
        """Return the icon."""
        return self._icon
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        earthquake_data = await self._fetch_earthquake_data()
        if earthquake_data:
            self._state = earthquake_data.get("magnitude")
            self._attributes = earthquake_data
        
    async def _fetch_earthquake_data(self):
        """Fetch latest earthquake data."""
        url = "https://api.gael.cl/general/public/sismos"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    if data and len(data) > 0:
                        latest = data[0]
                        return {
                            "magnitude": latest.get("Magnitud"),
                            "depth": latest.get("Profundidad"),
                            "location": latest.get("RefGeografica"),
                            "date": latest.get("Fecha"),
                            "latitude": latest.get("Latitud"),
                            "longitude": latest.get("Longitud")
                        }
                    return None
        except Exception as e:
            _LOGGER.error("Error fetching earthquake data: %s", e)
            return None
