#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/8/30 15:03
@File   :   account_entity.py
"""
from enum import Enum


class AccountStatus(str, Enum):
    """账户状态类型枚举"""

    ACTIVE = "active"  # 激活账号
    BANNED = "banned"  # 封禁账号
