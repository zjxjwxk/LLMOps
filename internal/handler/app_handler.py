#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 17:31
@File   :   app_handler.py
"""
import uuid
from dataclasses import dataclass

from injector import inject
from openai import OpenAI

from internal.exception import NotFoundException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import validate_error_json, success_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    appService: AppService

    def create_app(self):
        """创建应用"""
        app = self.appService.create_app()
        return success_message(f"应用创建成功，id={app.id}")

    def get_app(self, id: uuid.UUID):
        """查询应用"""
        app = self.appService.get_app(id)
        return success_message(f"应用获取成功，name={app.name}")

    def update_app(self, id: uuid.UUID):
        """更新应用"""
        app = self.appService.update_app(id)
        return success_message(f"应用更新成功，name={app.name}")

    def delete_app(self, id: uuid.UUID):
        """删除应用"""
        app = self.appService.delete_app(id)
        return success_message(f"应用删除成功，id={app.id}")

    def completion(self):
        """聊天接口"""

        # 1. 从POST请求中获取输入并校验
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

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
        return success_json({"content": content})

    def ping(self):
        raise NotFoundException("Pong not found")
        # return {"ping": "pong"}
