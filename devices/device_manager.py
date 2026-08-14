#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Device manager for multiple INA237 devices"""

from typing import List, Dict, Optional
from .ina237 import INA237


class DeviceManager:
    """Manages multiple INA237 devices"""

    def __init__(self, bus_driver):
        self.bus = bus_driver
        self.devices: Dict[int, INA237] = {}

    def discover_devices(self) -> List[int]:
        """Обнаружение всех устройств INA237 на шине (безопасное)"""
        addresses = []
        try:
            addresses = self.bus.scan_bus()
        except Exception as e:
            print(f"⚠️ Ошибка сканирования шины: {e}")
            return []

        for addr in addresses:
            try:
                if addr not in self.devices:
                    device = INA237(self.bus, addr)
                    if device.initialize():
                        self.devices[addr] = device
                        print(f"✅ Устройство по адресу 0x{addr:02X} инициализировано")
                    else:
                        print(f"⚠️ Не удалось инициализировать устройство 0x{addr:02X}")
            except Exception as e:
                print(f"⚠️ Ошибка при инициализации устройства 0x{addr:02X}: {e}")
                # Продолжаем со следующим устройством

        return addresses

    def get_device(self, address: int) -> Optional[INA237]:
        try:
            return self.devices.get(address)
        except Exception as e:
            print(f"⚠️ Ошибка получения устройства 0x{address:02X}: {e}")
            return None

    def get_all_devices(self) -> Dict[int, INA237]:
        try:
            return self.devices.copy()
        except Exception as e:
            print(f"⚠️ Ошибка получения списка устройств: {e}")
            return {}

    def remove_device(self, address: int) -> bool:
        try:
            if address in self.devices:
                del self.devices[address]
                return True
            return False
        except Exception as e:
            print(f"⚠️ Ошибка удаления устройства 0x{address:02X}: {e}")
            return False

    def get_device_list(self) -> List[Dict]:
        try:
            return [dev.get_info() for dev in self.devices.values()]
        except Exception as e:
            print(f"⚠️ Ошибка получения информации об устройствах: {e}")
            return []
