#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 18:18
@File   :   http.py
"""
from flask import Flask

from config import Config
from internal.router import Router


class Http(Flask):
    """HTTP服务引擎"""

    def __init__(self, *args, config: Config, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        # 注册应用路由
        router.register_router(self)

        # 注入配置
        self.config.from_object(config)
