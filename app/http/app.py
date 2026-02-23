#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 19:29
@File   :   app.py
"""
import dotenv
from injector import Injector

from config import Config
from internal.router import Router
from internal.server import Http

# 将.env文件加载到环境变量中
dotenv.load_dotenv()
config = Config()
injector = Injector()

app = Http(__name__, config=config, router=injector.get(Router))

if __name__ == "__name__":
    app.run(debug=True)
