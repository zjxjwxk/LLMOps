#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/24 16:43
@File   :   conftest.py
"""
import pytest

from app.http.app import app


@pytest.fixture
def client():
    """获取Flask测试应用实例"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
