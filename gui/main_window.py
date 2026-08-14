#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main window with demo/live mode support"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from config.constants import APP_TITLE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT
from config.settings import Settings
from core.driver_factory import DriverFactory
from devices.device_manager import DeviceManager
from .connection_panel import ConnectionPanel
from .device_panel import DevicePanel


class MainWindow:
    """Main application window"""

    def __init__(self, root: tk.Tk, demo_mode: bool = False):
        self.root = root
        self.demo_mode = demo_mode

        # Формируем заголовок
        if self.demo_mode:
            mode_str = " [ДЕМО-РЕЖИМ]"
        else:
            mode_str = " [БОЕВОЙ РЕЖИМ]"

        self.root.title(f"{APP_TITLE} v{APP_VERSION}{mode_str}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.settings = Settings()
        self.bus = None
        self.device_manager = None
        self.device_panels = {}
        self.auto_connect_done = False

        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Автоматическое подключение
        if self.demo_mode:
            self.root.after(500, self._auto_connect_demo)
        else:
            self.root.after(500, self._auto_connect_live)

    def _setup_ui(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        # Индикатор режима
        if self.demo_mode:
            mode_label = ttk.Label(top_frame, text="🔷 ДЕМО-РЕЖИМ",
                                  font=('Arial', 12, 'bold'),
                                  foreground='#D32F2F')
            mode_label.pack(side=tk.LEFT, padx=10)
        else:
            mode_label = ttk.Label(top_frame, text="🔴 БОЕВОЙ РЕЖИМ",
                                  font=('Arial', 12, 'bold'),
                                  foreground='#1B5E20')
            mode_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(top_frame, text="|", font=('Arial', 12)).pack(side=tk.LEFT)

        # Connection panel
        self.connection_panel = ConnectionPanel(top_frame, self, self.demo_mode)
        self.connection_panel.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Notebook для устройств
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаём начальную страницу с подсказкой
        self._create_empty_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_empty_tab(self):
        """Создание пустой вкладки с подсказкой"""
        self.empty_tab = ttk.Frame(self.notebook)

        if self.demo_mode:
            msg = "🔷 ДЕМО-РЕЖИМ: Подключение к симулятору..."
        else:
            msg = "🔴 БОЕВОЙ РЕЖИМ: Поиск оборудования..."

        ttk.Label(self.empty_tab, text=msg,
                 font=('Arial', 14)).pack(pady=50)
        self.notebook.add(self.empty_tab, text="Нет устройств")

    def _update_empty_tab(self, msg):
        """Обновить текст на пустой вкладке"""
        for child in self.empty_tab.winfo_children():
            child.destroy()
        ttk.Label(self.empty_tab, text=msg,
                 font=('Arial', 14)).pack(pady=50)

    def _auto_connect_demo(self):
        """Автоматическое подключение в демо-режиме"""
        if self.connection_panel.connect_demo():
            self.set_status("🔷 ДЕМО-РЕЖИМ: Симулятор INA237 активен")
            self.root.after(500, self.connection_panel.scan_demo)

    def _auto_connect_live(self):
        """Автоматическое подключение в боевом режиме"""
        if self.auto_connect_done:
            return
        self.auto_connect_done = True

        print("\n" + "="*60)
        print("🔴 БОЕВОЙ РЕЖИМ: ПОИСК ОБОРУДОВАНИЯ")
        print("="*60)

        # Проверяем установку pyftdi
        try:
            import pyftdi
            has_ftdi = True
            print("✅ pyftdi установлен")
        except ImportError:
            has_ftdi = False
            print("⚠️ pyftdi не установлен. Установите: pip install pyftdi")

        # Проверяем установку ch341dll
        try:
            import ch341dll
            has_ch341 = True
            print("✅ ch341dll установлен")
        except ImportError:
            has_ch341 = False
            print("⚠️ ch341dll не установлен")

        # Проверяем paramiko
        try:
            import paramiko
            has_paramiko = True
            print("✅ paramiko установлен")
        except ImportError:
            has_paramiko = False
            print("⚠️ paramiko не установлен. Установите: pip install paramiko")

        print("-"*60)

        # Пробуем FTDI (если установлен)
        if has_ftdi:
            print("\n🔍 Попытка подключения через FTDI FT232H...")
            self.set_status("🔍 Поиск FTDI FT232H...")
            self.root.update()

            try:
                from core.ftdi_driver import FTDIDriver
                ftdi = FTDIDriver()
                if ftdi.connect():
                    self.bus = ftdi
                    print("✅ Подключено через FTDI FT232H")
                    self.set_status("✅ Подключено через FTDI FT232H")
                    self._on_connected()
                    return
                else:
                    print("❌ FTDI FT232H не найден")
            except Exception as e:
                print(f"❌ Ошибка FTDI: {e}")
        else:
            print("\n⚠️ Пропуск FTDI (библиотека не установлена)")

        # Пробуем CH341 (если установлен)
        if has_ch341:
            print("\n🔍 Попытка подключения через CH341T...")
            self.set_status("🔍 Поиск CH341T...")
            self.root.update()

            try:
                from core.ch341_driver import CH341Driver
                ch341 = CH341Driver()
                if ch341.connect():
                    self.bus = ch341
                    print("✅ Подключено через CH341T")
                    self.set_status("✅ Подключено через CH341T")
                    self._on_connected()
                    return
                else:
                    print("❌ CH341T не найден")
            except Exception as e:
                print(f"❌ Ошибка CH341: {e}")
        else:
            print("\n⚠️ Пропуск CH341 (библиотека не установлена)")

        # Если paramiko установлен - предлагаем Ethernet
        if has_paramiko:
            print("\n🔍 Попытка подключения через Ethernet...")
            self.set_status("⚠️ FTDI/CH341 не найдены. Используйте Ethernet.")
            self.root.after(500, self._show_ethernet_dialog)
        else:
            # Если paramiko не установлен - просто показываем статус, без модальных окон
            print("\n❌ paramiko не установлен. Ethernet недоступен.")
            self.set_status("❌ FTDI/CH341 не найдены, paramiko не установлен")
            self.auto_connect_done = False
            self._update_empty_tab(
                "Оборудование не найдено\n\n"
                "Нажмите 'Подключить' для ручного выбора интерфейса\n"
                "или установите необходимые библиотеки."
            )

    def _show_ethernet_dialog(self):
        """Показать диалог подключения по Ethernet"""
        from .connection_panel import EthernetDialog

        print("\n" + "="*60)
        print("📋 ПОКАЗ ДИАЛОГА ETHERNET")
        print("="*60)

        dialog = EthernetDialog(self.root)

        print(f"📊 Результат диалога: {dialog.result}")

        if dialog.result is not None:  # Пользователь нажал OK
            print("✅ Пользователь нажал Подключиться")
            print(f"📝 Данные: {dialog.host}:{dialog.slot} (user: {dialog.username}")

            # Формируем строку подключения
            path = f"{dialog.host}:{dialog.slot}:{dialog.username}:{dialog.password}"
            self.set_status(f"🔌 Подключение к {dialog.host}...")
            self.root.update()

            # Пытаемся подключиться
            if self.connect("ethernet", path):
                print(f"✅ Подключено через Ethernet: {dialog.host}")
                self.set_status(f"✅ Подключено через Ethernet: {dialog.host}")
                self._on_connected()
            else:
                print(f"❌ Ошибка подключения к {dialog.host}")
                self.set_status(f"❌ Ошибка подключения к {dialog.host}")
                self.auto_connect_done = False
                # Не показываем модальное окно, просто обновляем статус
                self._update_empty_tab(
                    f"Не удалось подключиться к {dialog.host}\n\n"
                    "Проверьте параметры подключения и нажмите 'Подключить'"
                )
        else:
            # Пользователь отменил
            print("❌ Пользователь отменил Ethernet подключение")
            self.set_status("🔴 БОЕВОЙ РЕЖИМ: Ожидание ручного подключения")
            self.auto_connect_done = False
            self._update_empty_tab("Нажмите 'Подключить' для ручного подключения")
        print("="*60 + "\n")

    def _on_connected(self):
        """Действия после успешного подключения"""
        print("✅ Подключение установлено, выполняется сканирование...")
        self.connection_panel._set_connected_state()
        self.root.after(1000, self.connection_panel._scan)

    def connect(self, interface_type: str, device_path: str) -> bool:
        print(f"\n🔄 Подключение к интерфейсу: {interface_type}")
        print(f"📝 Параметры: {device_path}")

        try:
            self.bus = DriverFactory.create_driver(interface_type, device_path)
            if self.bus and self.bus.is_connected():
                print(f"✅ Подключено к {interface_type}")
                self.set_status(f"Подключено к {interface_type}")
                return True
            else:
                print(f"❌ Не удалось подключиться к {interface_type}")
                self.set_status(f"❌ Не удалось подключиться к {interface_type}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            import traceback
            traceback.print_exc()
            self.set_status(f"❌ Ошибка: {str(e)[:50]}...")
            return False

    def disconnect(self):
        if self.bus:
            self.bus.disconnect()
            self.bus = None
        self.device_manager = None
        self.device_panels.clear()
        self._clear_device_tabs()
        self._create_empty_tab()
        self.set_status("Отключено")
        self.auto_connect_done = False

    def scan_devices(self):
        """Сканирование устройств без параметров"""
        if not self.bus or not self.bus.is_connected():
            self.set_status("❌ Нет подключения")
            return

        try:
            self.device_manager = DeviceManager(self.bus)
            addresses = self.device_manager.discover_devices()

            self._clear_device_tabs()
            self.device_panels.clear()

            if not addresses:
                self.set_status("⚠️ Устройства INA237 не найдены")
                self._create_empty_tab()
                return

            for addr in addresses:
                device = self.device_manager.get_device(addr)
                if device:
                    panel = DevicePanel(self.notebook, device, self.demo_mode)
                    self.notebook.add(panel, text=f"INA237 0x{addr:02X}")
                    self.device_panels[addr] = panel

            self.set_status(f"✅ Найдено {len(addresses)} устройств(а)")

        except Exception as e:
            print(f"⚠️ Ошибка сканирования: {e}")
            self.set_status(f"⚠️ Ошибка сканирования: {str(e)[:50]}...")
            # Всё равно показываем пустую вкладку
            self._clear_device_tabs()
            self._create_empty_tab()

    def _clear_device_tabs(self):
        for i in range(self.notebook.index("end"), -1, -1):
            try:
                self.notebook.forget(i)
            except:
                pass

    def set_status(self, message: str):
        self.status_var.set(message)

    def on_closing(self):
        self.disconnect()
        self.root.destroy()
