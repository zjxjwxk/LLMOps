#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/24 16:43
@File   :   conftest.py
"""
import pytest
from sqlalchemy.orm import sessionmaker, scoped_session

from app.http.app import app as _app
from internal.extension.database_extension import db as _db


@pytest.fixture
def app():
    """获取Flask应用实例"""
    _app.config["TESTING"] = True
    return _app


@pytest.fixture
def client(app):
    """获取Flask测试客户端实例"""
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app):
    """创建临时数据库会话，测试结束后回滚数据"""
    with app.app_context():
        # 获取数据库连接并开启事务
        connection = _db.engine.connect()
        transaction = connection.begin()

        # 创建临时数据库会话
        session_factory = sessionmaker(bind=connection)
        session = scoped_session(session_factory)
        _db.session = session

        # 抛出数据库实例
        yield _db

        # 回滚数据
        transaction.rollback()
        # 关闭数据库连接
        connection.close()
        # 清除会话
        session.remove()
