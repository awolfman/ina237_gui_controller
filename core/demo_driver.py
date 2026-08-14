#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Demo driver for INA237 simulation"""

import random
import time
from typing import Optional, List
from .bus_driver import I2CBusDriver


class DemoDriver(I2CBusDriver):
    """Демо-драйвер для симуляции INA237"""

    def __init__(self):
        self.connected = False
        self.device_path = "demo"
        self.registers = {}
        self._init_registers()
        self._last_update = time.time()

    def _init_registers(self):
        """Инициализация регистров"""
        self.registers = {
            0x00: 0x0000,      # CONFIG
            0x01: 0x0A0A,      # ADC_CONFIG
            0x02: 0x1000,      # SHUNT_CAL
            0x04: 0x0000,      # VSHUNT
            0x05: 0x0A00,      # VBUS (~5V)
            0x06: 0x0064,      # DIETEMP (~25°C)
            0x07: 0x0000,      # CURRENT
            0x08: 0x00000000,  # POWER (32-bit)
            0x0B: 0x0000,      # DIAG_ALERT
            0x3E: 0x5449,      # MANUFACTURER_ID (TI)
            0x3F: 0x0000,      # DEVICE_ID
        }
        print(f"🔷 ДЕМО: Инициализированы регистры")

    def _update_measurements(self):
        """Обновление измерений с плавными изменениями"""
        # Генерируем реалистичные значения
        vbus = 1.0 + random.uniform(0, 10)
        current = random.uniform(-2, 15)

        # Конвертируем в raw значения
        vbus_raw = int(vbus / 0.003125)  # VBUS LSB = 3.125 mV
        current_raw = int(current / (20.0 / 32768.0))  # current_lsb = max_current / 32768

        self.registers[0x05] = vbus_raw & 0xFFFF
        self.registers[0x07] = current_raw & 0xFFFF

        # POWER (32-bit)
        power_raw = int((vbus * abs(current)) / (0.2 * (20.0 / 32768.0)))
        self.registers[0x08] = power_raw & 0xFFFFFFFF

        self.registers[0x04] = int(current_raw * 0.1) & 0xFFFF
        self.registers[0x06] = int(25 + random.uniform(-5, 15))  # Температура ~25°C

        self._last_update = time.time()

    def connect(self, device_path: Optional[str] = None) -> bool:
        self.connected = True
        self.device_path = device_path or "demo"
        print(f"🔷 ДЕМО-РЕЖИМ: Подключено к симулятору INA237")
        return True

    def disconnect(self) -> None:
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def write_register(self, address: int, reg_addr: int, value: int) -> bool:
        if reg_addr in [0x04, 0x05, 0x06, 0x07, 0x08, 0x3E, 0x3F]:
            return False
        self.registers[reg_addr] = value & 0xFFFF
        return True

    def read_register(self, address: int, reg_addr: int) -> Optional[int]:
        self._update_measurements()
        return self.registers.get(reg_addr, 0x0000)

    def read_register_32(self, address: int, reg_addr: int) -> Optional[int]:
        """Чтение 32-битного регистра для демо"""
        self._update_measurements()
        return self.registers.get(reg_addr, 0x00000000)

    def scan_bus(self) -> List[int]:
        return [0x40, 0x41, 0x42]
