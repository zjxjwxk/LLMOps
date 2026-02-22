#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 17:50
@File   :   router.py
"""
from dataclasses import dataclass

from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler


@inject
@dataclass
class Router:
    app_handler: AppHandler

    def register_router(self, app: Flask):
        """注册路由"""

        # 1. 创建一个蓝图
        blue_print = Blueprint("llmops", __name__, url_prefix="")

        # 2. 将url与对应的控制器方法绑定
        blue_print.add_url_rule("/ping", view_func=self.app_handler.ping)

        # 3. 在应用上注册蓝图
        app.register_blueprint(blue_print)
