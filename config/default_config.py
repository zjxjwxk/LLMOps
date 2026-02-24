#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/24 23:21
@File   :   default_config.py
"""
# 应用默认配置
DEFAULT_CONFIG = {
    # Flask-WTF配置
    "WTF_CSRF_ENABLED": "False",

    # SQLAlchemy数据库配置
    "SQLALCHEMY_DATABASE_URI": "",
    "SQLALCHEMY_POOL_SIZE": 30,
    "SQLALCHEMY_POOL_RECYCLE": 3600,
    "SQLALCHEMY_ECHO": "True"
}
