#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
INA237 Controller - Main Entry Point
"""

import sys
import os
import argparse
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.logger import setup_logger


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="INA237 Controller - Power Monitor Control Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python3 main.py              # Боевой режим (реальное оборудование)
  python3 main.py --demo       # Демо-режим (симулятор)
        """
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Запуск в демо-режиме (симулятор INA237)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='INA237 Controller v2.0'
    )

    return parser.parse_args()


def main():
    """Main application entry point"""
    # Парсим аргументы
    args = parse_args()

    # Определяем режим
    demo_mode = args.demo

    if demo_mode:
        print("🔷 ДЕМО-РЕЖИМ: работа с симулятором INA237")
    else:
        print("🔴 БОЕВОЙ РЕЖИМ: работа с реальным оборудованием")
        print("   (при отсутствии FTDI/CH341 будет использован Ethernet)")

    # Настройка логирования
    logger = setup_logger()
    logger.info(f"Starting INA237 Controller (Demo: {demo_mode})")

    # Создаём GUI
    root = tk.Tk()
    app = MainWindow(root, demo_mode=demo_mode)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Запускаем приложение
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()
