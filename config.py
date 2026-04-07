# -*- coding: utf-8 -*-
"""数据库配置 — SQLite 零配置"""
import os
import sys

# PyInstaller 打包后，__file__ 指向临时目录，需要用 sys.executable 定位 exe 真实位置
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "data.db")
