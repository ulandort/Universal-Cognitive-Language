#!/usr/bin/env python3
"""Compatibility CLI for the UCL/2.0 implementation in src/portable.py.

All normative Portable encoding and validation lives in src/. This small
entry point preserves existing documented commands and research imports.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import portable as _portable
from portable import *

def __getattr__(name):
    return getattr(_portable,name)

if __name__=='__main__':
    _portable.run_cli()
