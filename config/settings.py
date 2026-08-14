import json
import os
from .constants import DEFAULT_I2C_ADDRESS, DEFAULT_SHUNT_RESISTOR

class Settings:
    def __init__(self, config_file=None):
        self.config_file = config_file or "settings.json"
        self.settings = {}
        self._load_defaults()
        self._load()

    def _load_defaults(self):
        self.settings = {
            'interface_type': 'ftdi',
            'device_path': '',
            'i2c_address': DEFAULT_I2C_ADDRESS,
            'shunt_resistor': DEFAULT_SHUNT_RESISTOR,
            'max_current': 15.0,
            'monitor_interval': 1000,
            'theme': 'light',
            'demo_mode': True,
        }

    def _load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass

    def save(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except:
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    @property
    def interface_type(self):
        return self.get('interface_type', 'ftdi')

    @property
    def device_path(self):
        return self.get('device_path', '')

    @property
    def i2c_address(self):
        return self.get('i2c_address', DEFAULT_I2C_ADDRESS)

    @property
    def shunt_resistor(self):
        return self.get('shunt_resistor', DEFAULT_SHUNT_RESISTOR)

    @property
    def max_current(self):
        return self.get('max_current', 15.0)

    @property
    def monitor_interval(self):
        return self.get('monitor_interval', 1000)

    @property
    def demo_mode(self):
        return self.get('demo_mode', True)
