#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Device panel for INA237"""

import tkinter as tk
from tkinter import ttk
from devices.ina237 import INA237
from .register_editor import RegisterEditor


class DevicePanel(ttk.Frame):
    """Panel for a single INA237 device"""

    def __init__(self, parent, device: INA237, is_demo: bool = False):
        super().__init__(parent)
        self.device = device
        self.is_demo = is_demo
        self.monitoring = False

        try:
            self._create_widgets()
            self.read_all_registers()
        except Exception as e:
            print(f"⚠️ Ошибка создания панели устройства: {e}")
            self._create_error_panel(str(e))

    def _create_error_panel(self, error_msg: str):
        """Создание панели с сообщением об ошибке"""
        info_frame = ttk.LabelFrame(self, text="Ошибка устройства")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(info_frame, text=f"⚠️ Ошибка: {error_msg}",
                 foreground="red").pack(padx=5, pady=10)
        ttk.Label(info_frame, text="Нажмите 'Read All' для повторной попытки",
                 foreground="gray").pack(padx=5, pady=5)

    def _create_widgets(self):
        # Device info
        info_frame = ttk.LabelFrame(self, text="Информация об устройстве")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        try:
            info = self.device.get_info()
            # Всегда показываем ID: 0x5449 / INA237
            info_text = f"Адрес: {info['address']} | ID: {info['manufacturer_id']} / {info['device_id']}"
            ttk.Label(info_frame, text=info_text).pack(padx=5, pady=2)

            calib_status = "✅" if info.get('shunt_cal_read', False) else "⚠️"
            calib_text = (f"Current LSB: {info['current_lsb']} | "
                         f"Power LSB: {info['power_lsb']} | "
                         f"SHUNT_CAL: {calib_status}")
            ttk.Label(info_frame, text=calib_text, foreground="gray", font=('Arial', 8)).pack(padx=5, pady=2)
        except Exception as e:
            print(f"⚠️ Ошибка получения информации: {e}")
            # Показываем базовую информацию даже при ошибке
            ttk.Label(info_frame, text=f"Адрес: 0x{self.device.address:02X} | ID: INA237",
                     foreground="orange").pack(padx=5, pady=5)

        if self.is_demo:
            demo_label = ttk.Label(info_frame, text="🔷 ДЕМО-РЕЖИМ",
                                  foreground="#D32F2F", font=('Arial', 10, 'bold'))
            demo_label.pack(padx=5, pady=2)

        # Measurements
        meas_frame = ttk.LabelFrame(self, text="Измерения")
        meas_frame.pack(fill=tk.X, padx=5, pady=5)

        meas_grid = ttk.Frame(meas_frame)
        meas_grid.pack(fill=tk.X, padx=5, pady=5)

        self.measurements = {}
        meas_vars = [
            ("VBUS", "vbus", "V"),
            ("CURRENT", "current", "A"),
            ("POWER", "power", "W"),
            ("VSHUNT", "vshunt", "mV"),
            ("TEMP", "temp", "°C"),
        ]

        COLOR_MEAS = "#0D47A1"

        for i, (label, key, unit) in enumerate(meas_vars):
            row = i // 3
            col = (i % 3) * 3

            frame = ttk.Frame(meas_grid)
            frame.grid(row=row, column=col, padx=10, pady=3, sticky="w")

            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)
            var = tk.StringVar(value="---")
            ttk.Label(frame, textvariable=var, font=('Arial', 12, 'bold'),
                     foreground=COLOR_MEAS, width=12).pack(side=tk.LEFT, padx=5)
            ttk.Label(frame, text=unit, font=('Arial', 9)).pack(side=tk.LEFT)

            self.measurements[key] = var

        # Controls
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(ctrl_frame, text="📖 Read All",
                  command=self.read_all_registers).pack(side=tk.LEFT, padx=2)

        ttk.Button(ctrl_frame, text="📊 Read Measurements",
                  command=self.read_measurements).pack(side=tk.LEFT, padx=2)

        if self.is_demo:
            ttk.Button(ctrl_frame, text="🎲 Random Values",
                      command=self._randomize_demo).pack(side=tk.LEFT, padx=2)

        # Register editor
        reg_frame = ttk.LabelFrame(self, text="Регистры")
        reg_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        try:
            self.register_editor = RegisterEditor(reg_frame, self.device, self.is_demo)
            self.register_editor.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"⚠️ Ошибка создания редактора регистров: {e}")
            ttk.Label(reg_frame, text="⚠️ Редактор регистров недоступен",
                     foreground="red").pack(pady=20)

    def read_measurements(self):
        """Read and update measurements"""
        try:
            vbus = self.device.read_vbus()
            current = self.device.read_current()
            power = self.device.read_power()
            vshunt = self.device.read_vshunt()
            temp = self.device.read_temperature()

            if vbus is not None:
                self.measurements['vbus'].set(f"{vbus:.3f}")
            if current is not None:
                self.measurements['current'].set(f"{current:.3f}")
            if power is not None:
                self.measurements['power'].set(f"{power:.3f}")
            if vshunt is not None:
                self.measurements['vshunt'].set(f"{vshunt * 1000:.2f}")
            if temp is not None:
                self.measurements['temp'].set(f"{temp:.1f}")

        except Exception as e:
            print(f"⚠️ Ошибка чтения измерений: {e}")

    def _randomize_demo(self):
        """Generate random values for demo"""
        try:
            import random
            vbus = 1.0 + random.uniform(0, 10)
            current = random.uniform(-2, 15)
            power = vbus * current

            self.measurements['vbus'].set(f"{vbus:.3f}")
            self.measurements['current'].set(f"{current:.3f}")
            self.measurements['power'].set(f"{power:.3f}")
            self.measurements['vshunt'].set(f"{current * 1000:.2f}")
            self.measurements['temp'].set(f"{25 + random.uniform(-5, 15):.1f}")
        except Exception as e:
            print(f"⚠️ Ошибка генерации случайных значений: {e}")

    def read_all_registers(self):
        """Чтение всех регистров + калибровки"""
        try:
            # Сначала читаем калибровку
            if not self.is_demo:
                try:
                    self.device.read_calibration_from_device()
                except Exception as e:
                    print(f"⚠️ Ошибка чтения калибровки: {e}")

            # Затем читаем все регистры
            if hasattr(self, 'register_editor'):
                self.register_editor.read_all()
            self.read_measurements()
        except Exception as e:
            print(f"⚠️ Ошибка чтения всех регистров: {e}")
