#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""INA237 device class"""

from typing import Optional, Dict, Any
from .ina237_regs import INA237Regs
from config.constants import TI_MANUFACTURER_ID


class INA237:
    """INA237 power monitor device"""

    def __init__(self, bus_driver, address: int = 0x40):
        self.bus = bus_driver
        self.address = address
        self.initialized = False
        self.manufacturer_id = None
        self.device_id = None

        # Фиксированные параметры (как в вашем скрипте)
        self.max_current = 20.0
        self.current_lsb = self.max_current / 32768.0
        self.vbus_lsb = 3.125 * 10**(-3)
        self.dietemp_lsb = 125 * 10**(-3)
        self.power_lsb = 0.2 * self.current_lsb
        self.vshunt_lsb = 15.625 * 10**(-6)
        self.shunt_cal_read = False

        print(f"📊 Параметры расчёта для адреса 0x{self.address:02X}:")
        print(f"   Max Current: {self.max_current} A")
        print(f"   Current LSB: {self.current_lsb:.6f} A/bit")
        print(f"   Power LSB: {self.power_lsb:.6f} W/bit")
        print(f"   VBUS LSB: {self.vbus_lsb:.6f} V/bit")
        print(f"   DIETEMP LSB: {self.dietemp_lsb:.3f} °C/bit")

    def twos_comp(self, val: int, bits: int) -> int:
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    def initialize(self) -> bool:
        try:
            self.manufacturer_id = self.read_register(INA237Regs.MANUFACTURER_ID)
            self.device_id = self.read_register(INA237Regs.DEVICE_ID)

            if self.manufacturer_id != TI_MANUFACTURER_ID:
                print(f"⚠️ Внимание: Неизвестный ID производителя: 0x{self.manufacturer_id:04X}")
                print(f"   Ожидалось: 0x{TI_MANUFACTURER_ID:04X} (Texas Instruments)")
                return False

            print(f"✅ Устройство INA237 обнаружено (адрес: 0x{self.address:02X})")
            self.initialized = True
            self.read_calibration_from_device()
            return True

        except Exception as e:
            print(f"⚠️ Ошибка инициализации устройства 0x{self.address:02X}: {e}")
            return False

    def read_calibration_from_device(self) -> bool:
        try:
            shunt_cal = self.read_register(INA237Regs.SHUNT_CAL)
            if shunt_cal is not None:
                print(f"📊 Прочитан SHUNT_CAL: 0x{shunt_cal:04X}")
                self.shunt_cal_read = True
                return True
            else:
                print(f"⚠️ Не удалось прочитать SHUNT_CAL (адрес: 0x{self.address:02X})")
                self.shunt_cal_read = False
                return False
        except Exception as e:
            print(f"⚠️ Ошибка чтения SHUNT_CAL: {e}")
            self.shunt_cal_read = False
            return False

    def write_register(self, reg_addr: int, value: int) -> bool:
        try:
            if reg_addr in INA237Regs.READ_ONLY:
                return False
            return self.bus.write_register(self.address, reg_addr, value)
        except Exception as e:
            print(f"⚠️ Ошибка записи регистра 0x{reg_addr:02X}: {e}")
            return False

    def read_register(self, reg_addr: int) -> Optional[int]:
        try:
            return self.bus.read_register(self.address, reg_addr)
        except Exception as e:
            print(f"⚠️ Ошибка чтения регистра 0x{reg_addr:02X}: {e}")
            return None

    def read_register_32(self, reg_addr: int) -> Optional[int]:
        """Чтение 32-битного регистра с обработкой ошибок"""
        try:
            # Проверяем, есть ли у драйвера метод read_register_32
            if hasattr(self.bus, 'read_register_32'):
                return self.bus.read_register_32(self.address, reg_addr)
            else:
                # Если нет - пробуем прочитать 2 регистра по 16 бит
                print(f"⚠️ Драйвер не поддерживает read_register_32, пробуем 16-bit")
                low = self.read_register(reg_addr)
                high = self.read_register(reg_addr + 1)
                if low is not None and high is not None:
                    return (high << 16) | low
                return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения 32-bit регистра 0x{reg_addr:02X}: {e}")
            return None

    def read_vbus(self) -> Optional[float]:
        try:
            val = self.read_register(INA237Regs.VBUS)
            if val is not None:
                return val * self.vbus_lsb
            return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения VBUS: {e}")
            return None

    def read_current(self) -> Optional[float]:
        try:
            val = self.read_register(INA237Regs.CURRENT)
            if val is not None:
                current_sign = self.twos_comp(val, 16)
                return current_sign * self.current_lsb
            return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения CURRENT: {e}")
            return None

    def read_power(self) -> Optional[float]:
        """Чтение мощности (POWER) - 0x08 (32-битное значение)
        Power [W] = 0.2 x CURRENT_LSB x POWER
        POWER: биты 31-24 зарезервированы, действующие биты 23-0
        """
        try:
            val = self.read_register_32(INA237Regs.POWER)
            if val is not None:
                power_raw = val >> 8
                power = power_raw * self.power_lsb

                print(f"🔍 POWER отладка (32-bit):")
                print(f"   raw POWER (32-bit): 0x{val:08X} (десятичное: {val})")
                print(f"   power_raw (val >> 8): {power_raw} (0x{power_raw:06X})")
                print(f"   power_lsb: {self.power_lsb:.6f}")
                print(f"   POWER = {power_raw} * {self.power_lsb:.6f} = {power:.3f} W")

                return power
            else:
                print(f"⚠️ read_register_32 вернул None")
                return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения POWER: {e}")
            return None

    def read_vshunt(self) -> Optional[float]:
        try:
            val = self.read_register(INA237Regs.VSHUNT)
            if val is not None:
                return val * self.vshunt_lsb
            return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения VSHUNT: {e}")
            return None

    def read_temperature(self) -> Optional[float]:
        try:
            val = self.read_register(INA237Regs.DIETEMP)
            if val is not None:
                temp_sign = self.twos_comp(val >> 4, 12)
                return temp_sign * self.dietemp_lsb
            return None
        except Exception as e:
            print(f"⚠️ Ошибка чтения DIETEMP: {e}")
            return None

    def read_diag_alert(self) -> Optional[int]:
        try:
            return self.read_register(INA237Regs.DIAG_ALERT)
        except Exception as e:
            print(f"⚠️ Ошибка чтения DIAG_ALERT: {e}")
            return None

    def read_all_measurements(self) -> Dict[str, Optional[float]]:
        try:
            return {
                'vbus': self.read_vbus(),
                'current': self.read_current(),
                'power': self.read_power(),
                'vshunt': self.read_vshunt(),
                'temperature': self.read_temperature()
            }
        except Exception as e:
            print(f"⚠️ Ошибка чтения измерений: {e}")
            return {}

    def get_info(self) -> Dict[str, Any]:
        if self.manufacturer_id == TI_MANUFACTURER_ID:
            manuf_display = f"0x{self.manufacturer_id:04X}"
        elif self.manufacturer_id is not None:
            manuf_display = f"0x{self.manufacturer_id:04X} (?)"
        else:
            manuf_display = "N/A"

        return {
            'address': f"0x{self.address:02X}",
            'manufacturer_id': manuf_display,
            'device_id': "INA237",
            'initialized': self.initialized,
            'current_lsb': f"{self.current_lsb:.6f} A",
            'power_lsb': f"{self.power_lsb:.6f} W",
            'max_current': f"{self.max_current:.1f} A",
            'dietemp_lsb': f"{self.dietemp_lsb:.3f} °C",
            'shunt_cal_read': self.shunt_cal_read
        }
