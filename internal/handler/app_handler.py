#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 17:31
@File   :   app_handler.py
"""
from openai import OpenAI

from internal.schema.app_schema import CompletionReq


class AppHandler:
    """应用控制器"""

    def completion(self):
        """聊天接口"""

        # 1. 从POST请求中获取输入
        req = CompletionReq()
        if not req.validate():
            return req.errors

        # 2. 构建OpenAI客户端，并发起请求
        # （自动从环境变量获取 OPENAI_API_KEY 和 OPENAI_BASE_URL）
        client = OpenAI()

        # 3. 得到OpenAI响应，并返回给前端
        completion = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手"},
                {"role": "user", "content": req.query.data},
            ]
        )

        content = completion.choices[0].message.content
        return content

    def ping(self):
        return {"ping": "pong"}
