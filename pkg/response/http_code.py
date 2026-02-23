#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/23 17:21
@File   :   http_code.py
"""
from enum import Enum


class HttpCode(str, Enum):
    """HTTP业务状态码"""

    SUCCESS = "success"  # 成功状态
    FAIL = "fail"  # 失败状态
    VALIDATE_ERROR = "validate_error"  # 数据验证错误
    NOT_FOUND = "not_found"  # 未找到
    UNAUTHORIZED = "unauthorized"  # 未授权
    FORBIDDEN = "forbidden"  # 无权限
