#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 19:29
@File   :   app.py
"""
from injector import Injector

from internal.router import Router
from internal.server import Http

injector = Injector()

app = Http(__name__, router=injector.get(Router))

if __name__ == "__name__":
    app.run(debug=True)
