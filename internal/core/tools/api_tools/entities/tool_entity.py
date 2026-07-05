#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义API工具实体

@Author :   Xinkang Wu
@Time   :   2026/7/5 15:06
@File   :   tool_entity.py
"""
from pydantic import BaseModel, Field


class ToolEntity(BaseModel):
    """自定义API工具实体"""

    id: str = Field(default="", description="自定义API工具提供者id")
    name: str = Field(default="", description="自定义API工具名称")
    url: str = Field(default="", description="自定义API工具的请求地址")
    method: str = Field(default="", description="自定义API工具的请求方法")
    description: str = Field(default="", description="自定义API工具的描述")
    headers: list[dict] = Field(default_factory=list, description="自定义API工具的请求头列表")
    parameters: list[dict] = Field(default_factory=list, description="自定义API工具的参数列表")
