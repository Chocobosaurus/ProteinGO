#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 23:46:44 2023

@author: UZH-wezhon
"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    'ProteinGO.py',
    '--onefile',
    '--windowed'
    '--paths "/Users/UZH-wezhon/Desktop/ScientificaGameWZ"'
    ])