#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Personal Storage Manager - 启动入口"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
