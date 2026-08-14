#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FTDI FT232H I2C driver"""

import struct
from typing import Optional, List
from .bus_driver import I2CBusDriver

try:
    from pyftdi.i2c import I2cController
    FTDI_AVAILABLE = True
except ImportError:
    FTDI_AVAILABLE = False


class FTDIDriver(I2CBusDriver):
    """FTDI FT232H I2C bus driver"""

    def __init__(self):
        self.i2c = None
        self.connected = False
        self.device_path = None

    def connect(self, device_path=None):
        if not FTDI_AVAILABLE:
            print("pyftdi not installed. Install: pip install pyftdi")
            return False
        try:
            self.i2c = I2cController()
            if device_path:
                self.i2c.configure(device_path)
            else:
                self.i2c.configure('ftdi://ftdi:2232h/1')
            self.connected = True
            self.device_path = device_path
            return True
        except Exception as e:
            print(f"FTDI connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self.i2c:
            self.i2c = None
        self.connected = False

    def is_connected(self):
        return self.connected

    def write_register(self, address, reg_addr, value):
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            data = struct.pack('>H', value & 0xFFFF)
            self.i2c.write_to(address, bytes([reg_addr]) + data)
            return True
        except Exception as e:
            print(f"FTDI write error: {e}")
            return False

    def read_register(self, address, reg_addr):
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            self.i2c.write_to(address, bytes([reg_addr]))
            data = self.i2c.read_from(address, 2)
            if len(data) >= 2:
                return struct.unpack('>H', data[:2])[0]
            return None
        except Exception as e:
            print(f"FTDI read error: {e}")
            return None

    def read_register_32(self, address: int, reg_addr: int) -> Optional[int]:
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            self.i2c.write_to(address, bytes([reg_addr]))
            data = self.i2c.read_from(address, 4)
            if len(data) >= 4:
                return struct.unpack('>I', data[:4])[0]
            return None
        except Exception as e:
            print(f"FTDI read 32 error: {e}")
            return None

    def scan_bus(self):
        if not self.connected or not self.i2c:
            return []
        devices = []
        for addr in range(0x08, 0x78):
            try:
                self.i2c.write_to(addr, b'\x00')
                self.i2c.read_from(addr, 1)
                devices.append(addr)
            except:
                pass
        return devices
