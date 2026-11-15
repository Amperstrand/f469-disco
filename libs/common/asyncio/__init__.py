# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George

from .core import *

__version__ = (3, 0, 0)

_attrs = {
    "wait_for": "funcs",
    "gather": "funcs",
    "Event": "event",
    "Lock": "lock",
    "open_connection": "stream",
    "start_server": "stream",
    "StreamReader": "stream",
    "StreamWriter": "stream",
}

# Eager loader — the lazy module __getattr__ below requires a VM feature
# this micropython (v1.10-era) lacks: attributes like asyncio.Lock raised
# AttributeError on BOTH sim and device while asyncio.lock.Lock worked.
# Bench fix 2026-11-15: import eagerly, identical semantics on any VM.
for _attr, _mod in _attrs.items():
    globals()[_attr] = getattr(__import__(_mod, None, None, True, 1), _attr)
