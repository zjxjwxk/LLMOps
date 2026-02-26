#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 18:18
@File   :   http.py
"""

from flask import Flask

from config import Config
from internal.exception import CustomException
from internal.model import App
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """HTTP服务引擎"""

    def __init__(self, *args, db: SQLAlchemy, config: Config, router: Router, **kwargs):
        # 1. 调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 2. 初始化应用配置
        self.config.from_object(config)

        # 3. 注册异常处理器
        self.register_error_handler(Exception, self._error_handler)

        # 4. 初始化Flask扩展
        db.init_app(self)
        with self.app_context():
            _ = App()
            db.create_all()

        # 5. 注册应用路由
        router.register_router(self)

    def _error_handler(self, error: Exception):
        # 1. 自定义异常，返回对应异常信息作为响应
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {},
            ))

        # 2. 非自定义异常
        if self.debug:
            # Debug模式下，直接返回异常
            raise error
        else:
            # 非Debug模式下，提取异常信息作为message，统一返回FAIL响应
            return json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={},
            ))
