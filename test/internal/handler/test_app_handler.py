#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/24 16:22
@File   :   test_app_handler.py
"""
import pytest

from pkg.response import HttpCode


class TestAppHandler:
    """AppHandler测试类"""

    @pytest.mark.parametrize("query", [None, "你好，我叫李雷，1+1等于多少？"])
    def test_completion(self, query, client):
        response = client.post("/app/completion", json={"query": query})
        # 测试接口返回成功
        assert response.status_code == 200

        if query is None:
            # 测试数据校验失败
            assert response.json.get("code") == HttpCode.VALIDATE_ERROR
        else:
            # 测试completion返回成功
            assert response.json.get("code") == HttpCode.SUCCESS

        print("返回响应：", response.json)
