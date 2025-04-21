#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from finance_control.main import main

if __name__ == "__main__":
    main()