#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/7/20 14:02
@File   :   celery_extension.py
"""
from celery import Task, Celery
from flask import Flask


def init_app(app: Flask):
    """Celery配置服务初始化"""

    class FlaskTask(Task):
        """定义FlaskTask，使Celery在Flask应用的上下文中运行，以访问Flask和数据库等配置"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # 创建Celery应用并配置
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()

    # 将Celery挂载到Flask扩展中
    app.extensions["celery"] = celery_app
