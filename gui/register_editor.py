#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Register editor widget for INA237 with bit-field expansion"""

import tkinter as tk
from tkinter import ttk
from devices.ina237_regs import INA237Regs


class RegisterEditor(ttk.Frame):
    """Widget for editing INA237 registers with bit-field display"""

    def __init__(self, parent, device, is_demo: bool = False):
        super().__init__(parent)
        self.device = device
        self.is_demo = is_demo
        self.register_vars = {}
        self.bit_frames = {}
        self.bit_vars = {}
        self.expanded = {}
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Регистр", width=18).pack(side=tk.LEFT, padx=2)
        ttk.Label(header, text="Адрес", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(header, text="Значение", width=12).pack(side=tk.LEFT, padx=2)
        ttk.Label(header, text="Действия", width=18).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=2, pady=2)

        # Scrollable area
        canvas = tk.Canvas(self, height=280)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Register rows
        regs_to_show = [
            (INA237Regs.CONFIG, "CONFIG", "Настройка", INA237Regs.CONFIG_BITS, False),
            (INA237Regs.ADC_CONFIG, "ADC_CONFIG", "Настройка АЦП", INA237Regs.ADC_CONFIG_BITS, False),
            (INA237Regs.SHUNT_CAL, "SHUNT_CAL", "Калибровка шунта", None, False),
            (INA237Regs.VSHUNT, "VSHUNT", "Напряжение шунта", None, True),
            (INA237Regs.VBUS, "VBUS", "Напряжение шины", None, True),
            (INA237Regs.POWER, "POWER", "Мощность", None, True),
            (INA237Regs.CURRENT, "CURRENT", "Ток", None, True),
            (INA237Regs.DIETEMP, "DIETEMP", "Температура кристалла", None, True),
            (INA237Regs.DIAG_ALERT, "DIAG_ALERT", "Диагностика", INA237Regs.DIAG_ALERT_BITS, True),
            (INA237Regs.MANUFACTURER_ID, "MANUFACTURER_ID", "ID производителя", None, True),
            (INA237Regs.DEVICE_ID, "DEVICE_ID", "ID устройства", None, True),
        ]

        for reg_addr, reg_name, reg_desc, bit_defs, is_readonly in regs_to_show:
            # Основная строка
            row = ttk.Frame(scrollable)
            row.pack(fill=tk.X, padx=2, pady=2)

            # Имя с описанием
            name_label = ttk.Label(row, text=reg_name, width=18)
            name_label.pack(side=tk.LEFT, padx=2)

            # Адрес
            addr_label = ttk.Label(row, text=f"0x{reg_addr:02X}", width=8,
                                  foreground="gray")
            addr_label.pack(side=tk.LEFT, padx=2)

            # Значение
            var = tk.StringVar(value="----")
            entry = ttk.Entry(row, textvariable=var, width=12,
                            state='readonly' if is_readonly else 'normal')
            entry.pack(side=tk.LEFT, padx=2)

            self.register_vars[reg_addr] = var

            # Кнопки действий
            actions = ttk.Frame(row)
            actions.pack(side=tk.LEFT, padx=5)

            # Чтение
            read_btn = ttk.Button(actions, text="📖",
                                 command=lambda addr=reg_addr: self.read_register(addr),
                                 width=3)
            read_btn.pack(side=tk.LEFT, padx=1)

            # Запись
            if not is_readonly:
                write_btn = ttk.Button(actions, text="💾",
                                      command=lambda addr=reg_addr: self.write_register(addr),
                                      width=3)
                write_btn.pack(side=tk.LEFT, padx=1)

            # Кнопка раскрытия битов (если есть определение)
            if bit_defs:
                expand_btn = ttk.Button(actions, text="▼",
                                       command=lambda addr=reg_addr: self._toggle_bits(addr),
                                       width=3)
                expand_btn.pack(side=tk.LEFT, padx=1)
                self.expanded[reg_addr] = False

            # Метка (RO) для read-only
            if is_readonly:
                ro_label = ttk.Label(actions, text="(RO)",
                                    foreground="gray", font=('Arial', 8))
                ro_label.pack(side=tk.LEFT, padx=5)

            # Цветовое выделение для регистров измерений
            if reg_addr in [INA237Regs.VBUS, INA237Regs.CURRENT,
                           INA237Regs.POWER, INA237Regs.VSHUNT,
                           INA237Regs.DIETEMP]:
                name_label.config(foreground="#0D47A1", font=('Arial', 9, 'bold'))

            # DIAG_ALERT - не окрашиваем заранее
            if reg_addr == INA237Regs.DIAG_ALERT:
                name_label.config(font=('Arial', 9, 'bold'))

            # SHUNT_CAL - выделяем
            if reg_addr == INA237Regs.SHUNT_CAL:
                name_label.config(foreground="#E65100", font=('Arial', 9, 'bold'))

            # Фрейм для битов (изначально скрыт)
            bit_frame = ttk.Frame(scrollable)
            bit_frame.pack(fill=tk.X, padx=20, pady=2)
            bit_frame.pack_forget()
            self.bit_frames[reg_addr] = (bit_frame, bit_defs, var, name_label, is_readonly)
            self.bit_vars[reg_addr] = {}

    def _toggle_bits(self, reg_addr):
        """Раскрыть/скрыть биты регистра"""
        bit_frame, bit_defs, var, name_label, is_readonly = self.bit_frames[reg_addr]

        if self.expanded[reg_addr]:
            bit_frame.pack_forget()
            self.expanded[reg_addr] = False
        else:
            self._update_bit_display(reg_addr)
            bit_frame.pack(fill=tk.X, padx=20, pady=2)
            self.expanded[reg_addr] = True

    def _update_bit_display(self, reg_addr):
        """Обновить отображение битов"""
        bit_frame, bit_defs, var, name_label, is_readonly = self.bit_frames[reg_addr]

        # Очищаем фрейм
        for widget in bit_frame.winfo_children():
            widget.destroy()

        value_str = var.get()
        if value_str == "----":
            return

        try:
            value = int(value_str, 16)
        except:
            return

        # Для DIAG_ALERT проверяем аварии
        if reg_addr == INA237Regs.DIAG_ALERT:
            has_error = False
            has_warning = False
            for bit_pos, (bit_name, bit_desc, color) in bit_defs.items():
                bit_value = (value >> bit_pos) & 1
                if bit_value == 1:
                    if color == "red":
                        has_error = True
                    elif color == "yellow":
                        has_warning = True

            if has_error:
                name_label.config(foreground="#D32F2F")
            elif has_warning:
                name_label.config(foreground="#F57F17")
            else:
                name_label.config(foreground="#1B5E20")

        self.bit_vars[reg_addr] = {}

        # Отображаем биты
        for bit_pos, (bit_name, bit_desc, color) in sorted(bit_defs.items(), reverse=True):
            bit_value = (value >> bit_pos) & 1

            frame = ttk.Frame(bit_frame)
            frame.pack(fill=tk.X, padx=2, pady=1)

            can_edit = (reg_addr in [INA237Regs.CONFIG, INA237Regs.ADC_CONFIG]) and not is_readonly

            if color in ["red", "yellow", "green"]:
                if bit_value == 1:
                    if color == "red":
                        fg_color = "#C62828"
                        status_text = "⚠ АВАРИЯ!"
                    elif color == "yellow":
                        fg_color = "#F57F17"
                        status_text = "⚠ ПРЕДУПРЕЖДЕНИЕ"
                    else:
                        fg_color = "#1B5E20"
                        status_text = "✓ OK"
                else:
                    fg_color = "#9E9E9E"
                    status_text = "○ НОРМА"
            else:
                fg_color = "#1B5E20" if bit_value == 1 else "#9E9E9E"
                status_text = "● SET" if bit_value == 1 else "○ CLEAR"

            state_label = ttk.Label(frame, text=f"●",
                                   foreground=fg_color, font=('Arial', 10))
            state_label.pack(side=tk.LEFT, padx=2)

            ttk.Label(frame, text=f"Bit{bit_pos}: {bit_name}",
                     width=20, foreground=fg_color).pack(side=tk.LEFT, padx=2)

            if can_edit:
                bit_var = tk.IntVar(value=bit_value)
                self.bit_vars[reg_addr][bit_pos] = bit_var

                toggle_frame = ttk.Frame(frame)
                toggle_frame.pack(side=tk.LEFT, padx=2)

                btn_clear = ttk.Button(toggle_frame, text="0", width=2,
                                      command=lambda addr=reg_addr, pos=bit_pos: self._set_bit(addr, pos, 0))
                btn_clear.pack(side=tk.LEFT)

                bit_indicator = ttk.Label(toggle_frame, text=f" {bit_value} ",
                                         foreground=fg_color, font=('Arial', 9, 'bold'))
                bit_indicator.pack(side=tk.LEFT, padx=2)

                btn_set = ttk.Button(toggle_frame, text="1", width=2,
                                    command=lambda addr=reg_addr, pos=bit_pos: self._set_bit(addr, pos, 1))
                btn_set.pack(side=tk.LEFT)

                if bit_desc:
                    ttk.Label(frame, text=bit_desc,
                             foreground=fg_color, font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

                status_label = ttk.Label(frame, text=status_text,
                                        foreground=fg_color, font=('Arial', 8, 'bold'))
                status_label.pack(side=tk.LEFT, padx=5)

            else:
                ttk.Label(frame, text=f"= {bit_value}",
                         width=8, foreground=fg_color).pack(side=tk.LEFT, padx=2)

                if bit_desc:
                    ttk.Label(frame, text=bit_desc,
                             foreground=fg_color, font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

                if color in ["red", "yellow", "green"]:
                    status_label = ttk.Label(frame, text=status_text,
                                            foreground=fg_color, font=('Arial', 8, 'bold'))
                    status_label.pack(side=tk.LEFT, padx=5)

    def _set_bit(self, reg_addr, bit_pos, value):
        """Установить бит в регистре"""
        try:
            current_str = self.register_vars[reg_addr].get()
            current_value = int(current_str, 16)

            if value == 1:
                new_value = current_value | (1 << bit_pos)
            else:
                new_value = current_value & ~(1 << bit_pos)

            self.register_vars[reg_addr].set(f"0x{new_value:04X}")
            self._update_bit_display(reg_addr)

            print(f"🔧 Бит {bit_pos} установлен в {value} для регистра 0x{reg_addr:02X}")
        except Exception as e:
            print(f"❌ Ошибка установки бита: {e}")

    def read_register(self, reg_addr):
        """Read single register"""
        try:
            value = self.device.read_register(reg_addr)
            if value is not None:
                self.register_vars[reg_addr].set(f"0x{value:04X}")
                print(f"📖 Прочитан регистр 0x{reg_addr:02X} = 0x{value:04X}")

                if reg_addr in self.expanded and self.expanded[reg_addr]:
                    self._update_bit_display(reg_addr)
            else:
                print(f"❌ Ошибка чтения регистра 0x{reg_addr:02X}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def write_register(self, reg_addr):
        """Write single register"""
        try:
            value_str = self.register_vars[reg_addr].get()
            if value_str.startswith('0x'):
                value = int(value_str, 16)
            else:
                value = int(value_str, 16)

            if self.device.write_register(reg_addr, value):
                print(f"💾 Записан регистр 0x{reg_addr:02X} = 0x{value:04X}")
            else:
                print(f"❌ Ошибка записи регистра 0x{reg_addr:02X}")
        except ValueError:
            print("❌ Ошибка: неверный формат HEX (используйте 0x0000)")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def read_all(self):
        """Read all registers"""
        print("📖 Чтение всех регистров...")
        for reg_addr in self.register_vars.keys():
            try:
                value = self.device.read_register(reg_addr)
                if value is not None:
                    self.register_vars[reg_addr].set(f"0x{value:04X}")
            except Exception as e:
                print(f"❌ Ошибка чтения 0x{reg_addr:02X}: {e}")
        print("✅ Чтение завершено")
