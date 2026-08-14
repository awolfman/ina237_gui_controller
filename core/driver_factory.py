#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Driver factory"""

from typing import Optional
from .bus_driver import I2CBusDriver
from .ftdi_driver import FTDIDriver
from .ch341_driver import CH341Driver
from .demo_driver import DemoDriver
from .ethernet_driver import EthernetDriver


class DriverFactory:
    """Factory for creating I2C bus drivers"""

    _drivers = {
        'ftdi': FTDIDriver,
        'ch341': CH341Driver,
        'demo': DemoDriver,
        'ethernet': EthernetDriver,
    }

    @classmethod
    def create_driver(cls, interface_type: str, device_path: Optional[str] = None) -> Optional[I2CBusDriver]:
        """Создание драйвера по типу интерфейса"""
        driver_class = cls._drivers.get(interface_type.lower())
        if not driver_class:
            raise ValueError(f"Unsupported interface type: {interface_type}")
        driver = driver_class()
        driver.connect(device_path)
        return driver

    @classmethod
    def get_supported_interfaces(cls) -> list:
        """Получить список поддерживаемых интерфейсов"""
        return list(cls._drivers.keys())

    @classmethod
    def register_driver(cls, name: str, driver_class: type):
        """Зарегистрировать новый драйвер"""
        cls._drivers[name] = driver_class
