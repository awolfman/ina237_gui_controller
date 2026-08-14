#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Connection panel"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class EthernetDialog(simpledialog.Dialog):
    """Диалог для ввода параметров Ethernet подключения"""

    def __init__(self, parent, title="Ethernet Connection"):
        self.host = ""
        self.slot = "0"
        self.username = "root"
        self.password = ""
        super().__init__(parent, title)

    def body(self, master):
        # Заголовок
        ttk.Label(master, text="Введите параметры Ethernet подключения:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2,
                                                  padx=10, pady=10, sticky="w")

        # Хост
        ttk.Label(master, text="IP Адрес / Хост:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.host_entry = ttk.Entry(master, width=35)
        self.host_entry.grid(row=1, column=1, padx=10, pady=5)
        self.host_entry.insert(0, "192.168.1.100")
        self.host_entry.focus_set()

        # Slot (I2C шина)
        ttk.Label(master, text="Номер I2C шины (slot):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.slot_entry = ttk.Entry(master, width=35)
        self.slot_entry.grid(row=2, column=1, padx=10, pady=5)
        self.slot_entry.insert(0, "0")

        # Имя пользователя
        ttk.Label(master, text="Имя пользователя:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.user_entry = ttk.Entry(master, width=35)
        self.user_entry.grid(row=3, column=1, padx=10, pady=5)
        self.user_entry.insert(0, "root")

        # Пароль
        ttk.Label(master, text="Пароль (оставьте пустым если нет):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.pass_entry = ttk.Entry(master, width=35, show="*")
        self.pass_entry.grid(row=4, column=1, padx=10, pady=5)

        # Подсказка
        ttk.Label(master, text="Пример: 192.168.1.100:0:root:password",
                 foreground="gray", font=('Arial', 8)).grid(row=5, column=0, columnspan=2,
                                                            padx=10, pady=5)

        self.geometry("450x280")
        self.resizable(False, False)

        return self.host_entry

    def buttonbox(self):
        """Создание кнопок с нормальным размером"""
        box = ttk.Frame(self)

        ok_btn = tk.Button(box, text="Подключиться",
                          command=self.ok,
                          width=15, height=1,
                          bg='#4CAF50', fg='white',
                          font=('Arial', 10))
        ok_btn.pack(side=tk.LEFT, padx=5, pady=10)

        cancel_btn = tk.Button(box, text="Отмена",
                              command=self.cancel,
                              width=15, height=1,
                              bg='#f44336', fg='white',
                              font=('Arial', 10))
        cancel_btn.pack(side=tk.LEFT, padx=5, pady=10)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(pady=10)

    def ok(self, event=None):
        print("🔘 Нажата кнопка Подключиться")

        host = self.host_entry.get().strip()
        slot = self.slot_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not host:
            messagebox.showwarning("Ошибка", "Введите IP-адрес или имя хоста")
            return

        if not slot.isdigit():
            messagebox.showwarning("Ошибка", "Номер шины должен быть числом")
            return

        self.host = host
        self.slot = slot
        self.username = username
        self.password = password

        print(f"✅ Данные сохранены: {host}:{slot}")
        self.result = 1
        self.destroy()

    def cancel(self, event=None):
        print("🔘 Нажата кнопка Отмена")
        self.result = None
        self.destroy()


class ConnectionPanel(ttk.Frame):
    """Connection control panel"""

    def __init__(self, parent, app, is_demo_mode: bool = False):
        super().__init__(parent)
        self.app = app
        self.is_demo_mode = is_demo_mode
        self._create_widgets()

    def _create_widgets(self):
        # Interface
        ttk.Label(self, text="Интерфейс:").pack(side=tk.LEFT, padx=5)
        self.interface_var = tk.StringVar(value="demo" if self.is_demo_mode else "ftdi")
        interface_combo = ttk.Combobox(self, textvariable=self.interface_var,
                                      values=["ftdi", "ch341", "ethernet", "demo"],
                                      state="readonly", width=8)
        interface_combo.pack(side=tk.LEFT, padx=2)

        # Device path
        ttk.Label(self, text="Устройство:").pack(side=tk.LEFT, padx=5)
        self.device_path_var = tk.StringVar(value="")
        self.device_entry = ttk.Entry(self, textvariable=self.device_path_var, width=20)
        self.device_entry.pack(side=tk.LEFT, padx=2)

        # Кнопка настройки Ethernet
        self.eth_config_btn = ttk.Button(self, text="⚙ Настроить Ethernet",
                                        command=self._configure_ethernet)
        self.eth_config_btn.pack(side=tk.LEFT, padx=2)
        self.eth_config_btn.config(state=tk.DISABLED)

        # Shunt (оставляем для информации, но не используем)
        ttk.Label(self, text="Шунт (мОм):").pack(side=tk.LEFT, padx=5)
        self.shunt_var = tk.StringVar(value="5.0")
        ttk.Entry(self, textvariable=self.shunt_var, width=6, state='readonly').pack(side=tk.LEFT, padx=2)

        # Buttons
        self.connect_btn = ttk.Button(self, text="Подключить", command=self._connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = ttk.Button(self, text="Отключить",
                                        command=self._disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=2)

        self.scan_btn = ttk.Button(self, text="Scan", command=self._scan)
        self.scan_btn.pack(side=tk.LEFT, padx=2)

        # Monitor interval
        ttk.Label(self, text="Интервал (мс):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value="1000")
        ttk.Entry(self, textvariable=self.interval_var, width=6).pack(side=tk.LEFT, padx=2)

        self.monitor_btn = ttk.Button(self, text="▶ Монитор",
                                     command=self._toggle_monitor, state=tk.DISABLED)
        self.monitor_btn.pack(side=tk.LEFT, padx=2)

        # Индикатор режима
        if self.is_demo_mode:
            self.mode_indicator = ttk.Label(self, text="🔷 ДЕМО",
                                           foreground="#D32F2F", font=('Arial', 9, 'bold'))
        else:
            self.mode_indicator = ttk.Label(self, text="🔴 LIVE",
                                           foreground="#1B5E20", font=('Arial', 9, 'bold'))
        self.mode_indicator.pack(side=tk.LEFT, padx=10)

        interface_combo.bind('<<ComboboxSelected>>', self._on_interface_change)
        self._on_interface_change()

    def _on_interface_change(self, event=None):
        interface = self.interface_var.get()
        if interface == "ethernet":
            self.eth_config_btn.config(state=tk.NORMAL)
            self.device_entry.config(width=15)
            if not self.device_path_var.get():
                self.device_entry.delete(0, tk.END)
                self.device_entry.insert(0, "host:slot:user:pass")
        else:
            self.eth_config_btn.config(state=tk.DISABLED)
            self.device_entry.config(width=20)
            if interface == "demo" and not self.device_path_var.get():
                self.device_entry.delete(0, tk.END)
                self.device_entry.insert(0, "demo")
            elif interface in ["ftdi", "ch341"] and not self.device_path_var.get():
                self.device_entry.delete(0, tk.END)
                self.device_entry.insert(0, "")

    def _configure_ethernet(self):
        print("\n" + "="*60)
        print("📋 ОТКРЫТИЕ ДИАЛОГА ETHERNET")
        print("="*60)

        dialog = EthernetDialog(self)

        print(f"📊 Результат диалога: {dialog.result}")

        if dialog.result is not None:
            print("✅ Пользователь нажал Подключиться")
            print(f"📝 Данные: {dialog.host}:{dialog.slot} (user: {dialog.username})")

            path = f"{dialog.host}:{dialog.slot}:{dialog.username}:{dialog.password}"
            self.device_path_var.set(path)

            if dialog.password:
                self.app.set_status(f"Ethernet настроен: {dialog.host}:{dialog.slot} (с паролем)")
            else:
                self.app.set_status(f"Ethernet настроен: {dialog.host}:{dialog.slot} (без пароля)")

            print(f"📝 Строка подключения: {path}")
            print("="*60 + "\n")
        else:
            print("❌ Пользователь отменил диалог")
            print("="*60 + "\n")

    def _connect(self):
        interface = self.interface_var.get()
        device_path = self.device_path_var.get() or None

        if interface == "demo":
            self.connect_demo()
        else:
            if self.app.connect(interface, device_path):
                self._set_connected_state()

    def connect_demo(self):
        self.app.bus = None
        if self.app.connect("demo", "demo"):
            self._set_connected_state()
            self.app.set_status("🔷 ДЕМО-РЕЖИМ: Симулятор INA237 активен")
            return True
        return False

    def scan_demo(self):
        self._scan()

    def _set_connected_state(self):
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.scan_btn.config(state=tk.NORMAL)
        self.monitor_btn.config(state=tk.NORMAL)

    def _disconnect(self):
        self.app.disconnect()
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.DISABLED)
        self.monitor_btn.config(state=tk.DISABLED)
        self.monitor_btn.config(text="▶ Монитор")

    def _scan(self):
        """Сканирование без параметров"""
        self.app.scan_devices()

    def _toggle_monitor(self):
        if self.monitor_btn.cget("text") == "▶ Монитор":
            self.monitor_btn.config(text="⏹ Стоп")
            self.app.set_status("Мониторинг запущен")
            self._monitor_loop()
        else:
            self.monitor_btn.config(text="▶ Монитор")
            self.app.set_status("Мониторинг остановлен")

    def _monitor_loop(self):
        if self.monitor_btn.cget("text") == "⏹ Стоп":
            for addr, panel in self.app.device_panels.items():
                panel.read_measurements()
            try:
                interval = int(self.interval_var.get())
            except:
                interval = 1000
            self.after(min(interval, 5000), self._monitor_loop)
