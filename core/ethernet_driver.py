#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ethernet/SSH driver for remote INA237 access via paramiko"""

import socket
import time
import struct
from typing import Optional, List
from .bus_driver import I2CBusDriver

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


class EthernetDriver(I2CBusDriver):
    """SSH/Ethernet driver for remote I2C access"""

    def __init__(self):
        self.client = None
        self.connected = False
        self.host = None
        self.username = None
        self.password = None
        self.slot = 0
        self.endianness = None
        self.devices_cache = []

    def connect(self, device_path: Optional[str] = None) -> bool:
        if not PARAMIKO_AVAILABLE:
            print("paramiko не установлен. Установите: pip install paramiko")
            return False

        if not device_path:
            return False

        parts = device_path.split(':')
        if len(parts) < 4:
            self.host = parts[0] if len(parts) > 0 else "localhost"
            self.slot = int(parts[1]) if len(parts) > 1 else 0
            self.username = "root"
            self.password = ""
        else:
            self.host = parts[0]
            self.slot = int(parts[1])
            self.username = parts[2]
            self.password = parts[3] if len(parts) > 3 else ""

        try:
            print(f"Подключение к {self.host}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.password:
                self.client.connect(
                    hostname=self.host,
                    username=self.username,
                    password=self.password,
                    timeout=10
                )
            else:
                try:
                    self.client.connect(
                        hostname=self.host,
                        username=self.username,
                        timeout=10
                    )
                except paramiko.AuthenticationException:
                    self.client.connect(
                        hostname=self.host,
                        username=self.username,
                        password="",
                        timeout=10
                    )

            self.connected = True
            print(f"✅ Подключено к {self.host}")
            self._detect_endianness()
            return True

        except paramiko.AuthenticationException:
            print(f"❌ Ошибка аутентификации на {self.host}")
            self.connected = False
            return False
        except (socket.gaierror, socket.error) as e:
            print(f"❌ Ошибка подключения к {self.host}: {e}")
            self.connected = False
            return False
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            self.connected = False
            return False

    def _detect_endianness(self):
        if not self.connected:
            return

        for addr in range(0x40, 0x50):
            try:
                cmd = f"i2cget -y {self.slot} {hex(addr)} 0x3E w"
                success, output = self._run_cmd(cmd)
                if success and output:
                    clean = "".join(c for c in output if c.isalnum())
                    val = int(clean, 16)
                    if val == 0x5449:
                        self.endianness = 'big'
                        print(f"🔍 Обнаружен порядок байт: Big-Endian")
                        return
                    elif val == 0x4954:
                        self.endianness = 'little'
                        print(f"🔍 Обнаружен порядок байт: Little-Endian")
                        return
            except:
                continue

        self.endianness = 'big'
        print(f"⚠️ Не удалось определить порядок байт, используется Big-Endian")

    def _run_cmd(self, cmd: str) -> tuple:
        if not self.connected or not self.client:
            return False, "Not connected"

        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            error = stderr.read().decode().strip()
            output = stdout.read().decode().strip()
            if error:
                return False, error
            return True, output
        except Exception as e:
            return False, str(e)

    def _swap_bytes(self, val: int) -> int:
        low_byte = (val & 0xFF00) >> 8
        high_byte = (val & 0x00FF) << 8
        return high_byte | low_byte

    def disconnect(self) -> None:
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        self.connected = False
        print("🔌 Отключено")

    def is_connected(self) -> bool:
        return self.connected

    def write_register(self, address: int, reg_addr: int, value: int) -> bool:
        if not self.connected or not self.client:
            raise ConnectionError("Device not connected")

        try:
            val = self._swap_bytes(value) if self.endianness == 'little' else value
            cmd = f"i2cset -y {self.slot} {hex(address)} {hex(reg_addr)} {hex(val)} w"
            success, output = self._run_cmd(cmd)
            return success
        except Exception as e:
            print(f"❌ Ошибка записи: {e}")
            return False

    def read_register(self, address: int, reg_addr: int) -> Optional[int]:
        if not self.connected or not self.client:
            raise ConnectionError("Device not connected")

        try:
            cmd = f"i2cget -y {self.slot} {hex(address)} {hex(reg_addr)} w"
            success, output = self._run_cmd(cmd)

            if not success or not output:
                return None

            clean = "".join(c for c in output if c.isalnum())
            val = int(clean, 16)

            if self.endianness == 'little':
                val = self._swap_bytes(val)
            return val

        except Exception as e:
            print(f"❌ Ошибка чтения: {e}")
            return None

    def read_register_32(self, address: int, reg_addr: int) -> Optional[int]:
        """Читает 32-битное слово (режим 'd' - double word)"""
        if not self.connected or not self.client:
            raise ConnectionError("Device not connected")

        try:
            # Используем режим 'd' для 32-битного чтения
            cmd = f"i2cget -y {self.slot} {hex(address)} {hex(reg_addr)} d"
            print(f"🔍 Ethernet read_register_32: {cmd}")
            success, res = self._run_cmd(cmd)

            print(f"   success: {success}, res: '{res}'")

            if not success or not res:
                print(f"   ❌ Нет ответа, пробуем альтернативный способ")
                return self._read_register_32_alt(address, reg_addr)

            # Парсим вывод
            clean = "".join(c for c in res if c.isalnum() or c.isspace())
            parts = clean.split()
            print(f"   parts: {parts}")

            if len(parts) == 1:
                val = int(parts[0], 16)
            else:
                val = 0
                for part in parts:
                    val = (val << 8) | int(part, 16)

            print(f"   raw val: 0x{val:08X}")

            # Для режима 'd' данные приходят big-endian
            if self.endianness == 'little':
                val = ((val & 0xFF) << 24) | ((val & 0xFF00) << 8) | \
                      ((val & 0xFF0000) >> 8) | ((val & 0xFF000000) >> 24)
                print(f"   after swap: 0x{val:08X}")

            return val & 0xFFFFFFFF

        except Exception as e:
            print(f"❌ Ошибка чтения 32-bit: {e}")
            return None

    def _read_register_32_alt(self, address: int, reg_addr: int) -> Optional[int]:
        """Альтернативный способ чтения 32-битного слова (по 2 байта)"""
        try:
            print(f"🔍 Альтернативное чтение 32-bit по 16-битным словам...")

            # Читаем старшие 16 бит (регистр + 0)
            cmd1 = f"i2cget -y {self.slot} {hex(address)} {hex(reg_addr)} w"
            success1, res1 = self._run_cmd(cmd1)
            if not success1 or not res1:
                print(f"   ❌ Не удалось прочитать старшие 16 бит")
                return None

            # Читаем младшие 16 бит (регистр + 2)
            cmd2 = f"i2cget -y {self.slot} {hex(address)} {hex(reg_addr + 2)} w"
            success2, res2 = self._run_cmd(cmd2)
            if not success2 or not res2:
                print(f"   ❌ Не удалось прочитать младшие 16 бит")
                return None

            clean1 = "".join(c for c in res1 if c.isalnum())
            clean2 = "".join(c for c in res2 if c.isalnum())

            val1 = int(clean1, 16)
            val2 = int(clean2, 16)

            # Собираем 32-битное значение
            val = (val1 << 16) | val2

            print(f"   val1 (старшие): 0x{val1:04X}, val2 (младшие): 0x{val2:04X}")
            print(f"   итоговое val: 0x{val:08X}")

            if self.endianness == 'little':
                val = ((val & 0xFF) << 24) | ((val & 0xFF00) << 8) | \
                      ((val & 0xFF0000) >> 8) | ((val & 0xFF000000) >> 24)
                print(f"   after swap: 0x{val:08X}")

            return val & 0xFFFFFFFF
        except Exception as e:
            print(f"❌ Ошибка альтернативного чтения: {e}")
            return None

    def scan_bus(self) -> List[int]:
        if not self.connected or not self.client:
            return []

        devices = []
        for addr in range(0x08, 0x78):
            try:
                cmd = f"i2cget -y {self.slot} {hex(addr)} 0x3E w"
                success, output = self._run_cmd(cmd)
                if success and output:
                    clean = "".join(c for c in output if c.isalnum())
                    val = int(clean, 16)
                    if val == 0x5449 or val == 0x4954:
                        devices.append(addr)
                        if addr not in self.devices_cache:
                            self.devices_cache.append(addr)
            except:
                continue

        return devices

    def get_bus_info(self) -> str:
        status = "Подключено" if self.connected else "Отключено"
        endian = self.endianness if self.endianness else "Не определён"
        devices = len(self.devices_cache)
        return f"Ethernet: {self.host}:{self.slot} | Статус: {status} | Endianness: {endian} | Устройств: {devices}"
