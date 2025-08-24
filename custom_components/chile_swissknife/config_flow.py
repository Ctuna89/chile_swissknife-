"""Config flow for Chile Swissknife."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ChileSwissknifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chile Swissknife."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate input
            if "bus_stops" in user_input:
                bus_stops = [stop.strip() for stop in user_input["bus_stops"].split(",") if stop.strip()]
                user_input["bus_stops"] = bus_stops
            
            return self.async_create_entry(title="Chile Swissknife", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("bus_stops", default=""): str,
            vol.Optional("update_interval", default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "bus_stops_info": "Enter bus stop codes separated by commas (e.g., PA123, PA456)"
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ChileSwissknifeOptionsFlow(config_entry)


class ChileSwissknifeOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Chile Swissknife."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Validate input
            if "bus_stops" in user_input:
                bus_stops = [stop.strip() for stop in user_input["bus_stops"].split(",") if stop.strip()]
                user_input["bus_stops"] = bus_stops
            
            return self.async_create_entry(title="", data=user_input)

        bus_stops = self.config_entry.data.get("bus_stops", [])
        update_interval = self.config_entry.data.get("update_interval", 10)

        data_schema = vol.Schema({
            vol.Optional("bus_stops", default=", ".join(bus_stops)): str,
            vol.Optional("update_interval", default=update_interval): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "bus_stops_info": "Enter bus stop codes separated by commas (e.g., PA123, PA456)"
            }
        )
