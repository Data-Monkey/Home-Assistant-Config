"""
Support for Xiaomi sensors.

Developed by Rave from Lazcad.com
"""
import logging

try:
    from homeassistant.components.xiaomi import (PY_XIAOMI_GATEWAY, XiaomiDevice)
except ImportError:
    from custom_components.xiaomi import (PY_XIAOMI_GATEWAY, XiaomiDevice)
from homeassistant.const import TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Xiaomi devices."""
    devices = []
    gateways = PY_XIAOMI_GATEWAY.gateways
    for (ip_add, gateway) in gateways.items():
        for device in gateway.devices['sensor']:
            if device['model'] == 'sensor_ht':
                devices.append(XiaomiSensor(device, 'Temperature', 'temperature', gateway))
                devices.append(XiaomiSensor(device, 'Humidity', 'humidity', gateway))
            elif device['model'] == 'gateway':
                devices.append(XiaomiSensor(device, 'Illumination', 'illumination', gateway))
    add_devices(devices)


class XiaomiSensor(XiaomiDevice):
    """Representation of a XiaomiSensor."""

    def __init__(self, device, name, data_key, xiaomi_hub):
        """Initialize the XiaomiSensor."""
        self.current_value = None
        self._data_key = data_key
        self._battery = None
        XiaomiDevice.__init__(self, device, name, xiaomi_hub)

    @property
    def state(self):
        """Return the name of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        if self._data_key == 'temperature':
            return TEMP_CELSIUS
        elif self._data_key == 'humidity':
            return '%'
        elif self._data_key == 'illumination':
            return 'lm'

    def parse_data(self, data):
        """Parse data sent by gateway"""
        value = data.get(self._data_key)
        if value is None:
            return False
        value = int(value)
        if self._data_key == 'temperature' and value == 100:
            return False
        elif self._data_key == 'humidity' and value == 0:
            return False
        elif self._data_key == 'illumination' and value == 0:
            return False
        if self._data_key in ['temperature', 'humidity']:
            value = value / 100
        self.current_value = value  
        return True
