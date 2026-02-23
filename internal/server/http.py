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
from internal.router import Router
from pkg.response import json, Response, HttpCode


class Http(Flask):
    """HTTP服务引擎"""

    def __init__(self, *args, config: Config, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        # 注册应用路由
        router.register_router(self)

        # 注册异常处理
        self.register_error_handler(Exception, self._error_handler)

        # 注入配置
        self.config.from_object(config)

    def _error_handler(self, error: Exception):
        # 1. 自定义异常，返回对应异常信息作为响应
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data else {},
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
