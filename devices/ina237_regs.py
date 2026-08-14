#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""INA237 register definitions (по даташиту)"""


class INA237Regs:
    """INA237 register addresses (по даташиту)"""
    CONFIG = 0x00
    ADC_CONFIG = 0x01
    SHUNT_CAL = 0x02
    # 0x03 зарезервирован
    VSHUNT = 0x04
    VBUS = 0x05
    DIETEMP = 0x06          # Температура
    CURRENT = 0x07          # Ток
    POWER = 0x08            # Мощность
    # 0x09-0x0A зарезервированы
    DIAG_ALERT = 0x0B       # Диагностика и аварии
    SOVL = 0x0C             # Shunt Overvoltage Threshold
    SUVL = 0x0D             # Shunt Undervoltage Threshold
    BOVL = 0x0E             # Bus Overvoltage Threshold
    BUVL = 0x0F             # Bus Undervoltage Threshold
    TEMP_LIMIT = 0x10       # Temperature Limit
    PWR_LIMIT = 0x11        # Power Limit
    MANUFACTURER_ID = 0x3E
    DEVICE_ID = 0x3F

    REG_NAMES = {
        0x00: "CONFIG",
        0x01: "ADC_CONFIG",
        0x02: "SHUNT_CAL",
        0x04: "VSHUNT",
        0x05: "VBUS",
        0x06: "DIETEMP",
        0x07: "CURRENT",
        0x08: "POWER",
        0x0B: "DIAG_ALERT",
        0x0C: "SOVL",
        0x0D: "SUVL",
        0x0E: "BOVL",
        0x0F: "BUVL",
        0x10: "TEMP_LIMIT",
        0x11: "PWR_LIMIT",
        0x3E: "MANUFACTURER_ID",
        0x3F: "DEVICE_ID"
    }

    READ_ONLY = {
        0x04, 0x05, 0x06, 0x07, 0x08,  # Измерения
        0x0B,                           # DIAG_ALERT
        0x3E, 0x3F                      # ID
    }

    # DIAG_ALERT битовые поля (по даташиту)
    DIAG_ALERT_BITS = {
        15: ("TEMP_LIMIT", "Temperature Limit Exceeded", "red"),
        14: ("VSHUNT_OC", "Shunt Overcurrent", "red"),
        13: ("VBUS_OV", "Bus Overvoltage", "red"),
        12: ("VBUS_UV", "Bus Undervoltage", "yellow"),
        11: ("POWER_LIMIT", "Power Limit Exceeded", "yellow"),
        10: ("CURRENT_LIMIT", "Current Limit Exceeded", "yellow"),
        9: ("CONV_READY", "Conversion Ready", "green"),
        8: ("MATH_OVF", "Math Overflow", "red"),
        7: ("ADC_OVF", "ADC Overflow", "red"),
        6: ("MEM_ERR", "Memory Error", "red"),
        5: ("TEMP_HIGH", "Temperature High", "yellow"),
        4: ("TEMP_LOW", "Temperature Low", "green"),
        3: ("VSHUNT_OC_H", "Shunt OC High", "red"),
        2: ("VSHUNT_OC_L", "Shunt OC Low", "green"),
        1: ("VBUS_OV_H", "Bus OV High", "red"),
        0: ("VBUS_UV_L", "Bus UV Low", "yellow"),
    }

    # CONFIG битовые поля
    CONFIG_BITS = {
        15: ("RST", "Device Reset", None),
        14: ("RESERVED", "Reserved", None),
        13: ("CONV_MODE", "Conversion Mode (0=Continuous, 1=Triggered)", None),
        12: ("RESERVED", "Reserved", None),
        11: ("CTRL_LOOP", "Control Loop (0=Disabled, 1=Enabled)", None),
        10: ("RESERVED", "Reserved", None),
        9: ("RESERVED", "Reserved", None),
        8: ("RESERVED", "Reserved", None),
        7: ("RESERVED", "Reserved", None),
        6: ("RESERVED", "Reserved", None),
        5: ("RESERVED", "Reserved", None),
        4: ("RESERVED", "Reserved", None),
        3: ("RESERVED", "Reserved", None),
        2: ("RESERVED", "Reserved", None),
        1: ("RESERVED", "Reserved", None),
        0: ("RESERVED", "Reserved", None),
    }

    # ADC_CONFIG битовые поля
    ADC_CONFIG_BITS = {
        15: ("VBUS_AVG_3", "VBUS Average Bit 3", None),
        14: ("VBUS_AVG_2", "VBUS Average Bit 2", None),
        13: ("VBUS_AVG_1", "VBUS Average Bit 1", None),
        12: ("VBUS_AVG_0", "VBUS Average Bit 0", None),
        11: ("VBUS_CT_2", "VBUS Conv Time Bit 2", None),
        10: ("VBUS_CT_1", "VBUS Conv Time Bit 1", None),
        9: ("VBUS_CT_0", "VBUS Conv Time Bit 0", None),
        8: ("RESERVED", "Reserved", None),
        7: ("CURRENT_AVG_3", "Current Average Bit 3", None),
        6: ("CURRENT_AVG_2", "Current Average Bit 2", None),
        5: ("CURRENT_AVG_1", "Current Average Bit 1", None),
        4: ("CURRENT_AVG_0", "Current Average Bit 0", None),
        3: ("CURRENT_CT_2", "Current Conv Time Bit 2", None),
        2: ("CURRENT_CT_1", "Current Conv Time Bit 1", None),
        1: ("CURRENT_CT_0", "Current Conv Time Bit 0", None),
        0: ("RESERVED", "Reserved", None),
    }
