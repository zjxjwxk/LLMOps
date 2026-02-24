#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/25 00:09
@File   :   module.py
"""
from flask_sqlalchemy import SQLAlchemy
from injector import Module, Binder

from internal.extension.database_extension import db


class ExtensionModule(Module):
    """扩展模块的依赖注入"""

    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
