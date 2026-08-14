#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CH341T I2C driver"""

import struct
from typing import Optional, List
from .bus_driver import I2CBusDriver

try:
    import ch341dll
    CH341_AVAILABLE = True
except ImportError:
    CH341_AVAILABLE = False


class CH341Driver(I2CBusDriver):
    """CH341T I2C bus driver"""

    def __init__(self):
        self.i2c = None
        self.connected = False
        self.device_index = -1

    def connect(self, device_path=None):
        if not CH341_AVAILABLE:
            print("ch341dll not installed")
            return False
        try:
            self.i2c = ch341dll.CH341DLL()
            index = int(device_path) if device_path else 0
            if self.i2c.OpenDevice(index):
                self.connected = True
                self.device_index = index
                return True
            return False
        except Exception as e:
            print(f"CH341 connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self.i2c:
            try:
                self.i2c.CloseDevice()
            except:
                pass
            self.i2c = None
        self.connected = False

    def is_connected(self):
        return self.connected

    def write_register(self, address, reg_addr, value):
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            data = struct.pack('>H', value & 0xFFFF)
            result = self.i2c.WriteI2C(address, bytes([reg_addr]) + data)
            return result == len(data) + 1
        except Exception as e:
            print(f"CH341 write error: {e}")
            return False

    def read_register(self, address, reg_addr):
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            data = self.i2c.ReadI2C(address, reg_addr, 2)
            if len(data) >= 2:
                return struct.unpack('>H', data[:2])[0]
            return None
        except Exception as e:
            print(f"CH341 read error: {e}")
            return None

    def read_register_32(self, address: int, reg_addr: int) -> Optional[int]:
        if not self.connected or not self.i2c:
            raise ConnectionError("Device not connected")
        try:
            data = self.i2c.ReadI2C(address, reg_addr, 4)
            if len(data) >= 4:
                return struct.unpack('>I', data[:4])[0]
            return None
        except Exception as e:
            print(f"CH341 read 32 error: {e}")
            return None

    def scan_bus(self):
        if not self.connected or not self.i2c:
            return []
        devices = []
        for addr in range(0x08, 0x78):
            try:
                data = self.i2c.ReadI2C(addr, 0x00, 1)
                if data is not None and len(data) > 0:
                    devices.append(addr)
            except:
                pass
        return devices
