"""Sensor platform for Chile Swissknife."""
import asyncio
import logging
import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

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
    
    async_add_entities(sensors, True)


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


class USDClpSensor(ChileSwissknifeSensor):
    """Representation of a USD to CLP sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "USD to CLP"
        self._attr_native_unit_of_measurement = "CLP"
        self._attr_icon = "mdi:currency-usd"
        self._attr_unique_id = "usd_to_clp"
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        usd_data = await self._fetch_usd_data()
        self._state = usd_data.get("value")
        
    async def _fetch_usd_data(self):
        """Fetch USD to CLP data."""
        url = "https://mindicador.cl/api/dolar"
        try:
            async with async_timeout.timeout(10):
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
        self._attr_name = "UF to CLP"
        self._attr_native_unit_of_measurement = "CLP"
        self._attr_icon = "mdi:cash"
        self._attr_unique_id = "uf_to_clp"
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        uf_data = await self._fetch_uf_data()
        self._state = uf_data.get("value")
        
    async def _fetch_uf_data(self):
        """Fetch UF to CLP data."""
        url = "https://mindicador.cl/api/uf"
        try:
            async with async_timeout.timeout(10):
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
        self._attr_name = "Metro de Santiago Status"
        self._attr_icon = "mdi:subway"
        self._state = "Operational"
        self._attr_unique_id = "metro_status"
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        metro_data = await self._fetch_metro_status()
        self._state = metro_data.get("status", "Unknown")
        self._attr_extra_state_attributes = metro_data.get("lines", {})
        
    async def _fetch_metro_status(self):
        """Fetch Metro de Santiago status."""
        url = "https://www.metro.cl/api/estado-red"
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        data = await response.json()
                        status = "Operational"
                        lines = {}
                        
                        if "lines" in data:
                            for line in data.get("lines", []):
                                line_name = line.get("name", "Unknown")
                                line_status = line.get("status", "Unknown")
                                lines[line_name] = line_status
                                if line_status != "Operativa":
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
        self._attr_name = f"Bus Stop {stop_id}"
        self._attr_icon = "mdi:bus"
        self._state = None
        self._attr_unique_id = f"bus_stop_{stop_id}"
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        bus_data = await self._fetch_bus_data(self.stop_id)
        if "buses" in bus_data:
            self._state = len(bus_data.get("buses", []))
        else:
            self._state = 0
        self._attr_extra_state_attributes = bus_data
        
    async def _fetch_bus_data(self, stop_id):
        """Fetch bus data for a specific stop."""
        url = f"https://api.xor.cl/red/bus-stop/{stop_id}"
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            return {"error": f"HTTP {response.status}", "stop_id": stop_id}
        except Exception as e:
            _LOGGER.error("Error fetching bus data for stop %s: %s", stop_id, e)
            return {"error": str(e), "stop_id": stop_id}


class EarthquakeSensor(ChileSwissknifeSensor):
    """Representation of an earthquake sensor."""
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Latest Earthquake"
        self._attr_icon = "mdi:earthquake"
        self._state = None
        self._attr_unique_id = "latest_earthquake"
        
    async def async_update(self):
        """Update the sensor."""
        await super().async_update()
        earthquake_data = await self._fetch_earthquake_data()
        if earthquake_data and "magnitude" in earthquake_data:
            self._state = earthquake_data.get("magnitude")
            self._attr_extra_state_attributes = earthquake_data
        else:
            self._state = "No data"
            self._attr_extra_state_attributes = {}
        
    async def _fetch_earthquake_data(self):
        """Fetch latest earthquake data."""
        url = "https://api.gael.cl/general/public/sismos"
        try:
            async with async_timeout.timeout(10):
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
