#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/7/19 16:15
@File   :   redis_extension.py
"""
import redis
from flask import Flask
from redis import Connection, SSLConnection

redis_client = redis.Redis()


def init_app(app: Flask):
    """初始化Redis客户端"""

    # 根据不同场景，使用不同连接方式
    connection_class = Connection

    if app.config.get("REDIS_USE_SSL", False):
        connection_class = SSLConnection

    # 创建Redis连接池
    redis_client.connection_pool = redis.ConnectionPool(**{
        "host": app.config.get("REDIS_HOST", "127.0.0.1"),
        "port": app.config.get("REDIS_PORT", 6379),
        "username": app.config.get("REDIS_USERNAME", None),
        "password": app.config.get("REDIS_PASSWORD", None),
        "db": app.config.get("REDIS_DB", 0),
        "encoding_errors": "strict",
        "decode_responses": False
    }, connection_class=connection_class)

    app.extensions["redis"] = redis_client
