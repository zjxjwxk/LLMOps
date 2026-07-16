#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志记录器初始化

@Author :   Xinkang Wu
@Time   :   2026/7/16 16:06
@File   :   logging_extension.py
"""
import logging
import os.path
from logging.handlers import TimedRotatingFileHandler

from flask import Flask


def init_app(app: Flask):
    """日志记录器初始化"""

    # 设置日志存储文件夹
    log_folder = os.path.join(os.getcwd(), "storage", "log")

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 定义日志文件名
    log_file = os.path.join(log_folder, "app.log")

    # 设置日志格式，每天生成一份文件
    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(filename)s -> %(funcName)s -> line:%(lineno)d [%(levelname)s]: %(message)s"
    )

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logging.getLogger().addHandler(handler)

    # 开发环境下，同时将日志输出到控制台
    if app.debug or os.getenv("FLASK_ENV") == "development":
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
