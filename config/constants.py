#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Application constants"""

# I2C constants
DEFAULT_I2C_ADDRESS = 0x40
TI_MANUFACTURER_ID = 0x5449

# Device parameters
DEFAULT_SHUNT_RESISTOR = 0.001  # 1 mOhm
DEFAULT_MAX_CURRENT = 15.0      # 15A

# Monitoring
DEFAULT_MONITOR_INTERVAL = 1000  # ms

# GUI constants
APP_TITLE = "INA237 Controller"
APP_VERSION = "2.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Colors
COLOR_VBUS = "#2196F3"      # Blue
COLOR_CURRENT = "#4CAF50"   # Green
COLOR_POWER = "#F44336"     # Red
COLOR_VSHUNT = "#9C27B0"    # Purple
COLOR_TEMP = "#FF9800"      # Orange

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
