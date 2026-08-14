#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Abstract I2C bus driver interface"""

from abc import ABC, abstractmethod
from typing import Optional, List


class I2CBusDriver(ABC):
    """Abstract base class for I2C bus drivers"""

    @abstractmethod
    def connect(self, device_path: Optional[str] = None) -> bool:
        """Connect to I2C bus"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from I2C bus"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to bus"""
        pass

    @abstractmethod
    def write_register(self, address: int, reg_addr: int, value: int) -> bool:
        """Write 16-bit value to device register"""
        pass

    @abstractmethod
    def read_register(self, address: int, reg_addr: int) -> Optional[int]:
        """Read 16-bit value from device register"""
        pass

    @abstractmethod
    def read_register_32(self, address: int, reg_addr: int) -> Optional[int]:
        """Read 32-bit value from device register"""
        pass

    @abstractmethod
    def scan_bus(self) -> List[int]:
        """Scan I2C bus for devices"""
        pass
