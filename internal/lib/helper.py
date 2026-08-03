#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
辅助函数

@Author :   Xinkang Wu
@Time   :   2026/6/21 16:25
@File   :   helper.py
"""
import importlib
from hashlib import sha3_256
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
    """动态导入指定模块下的指定功能"""

    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)


def add_attribute(attr_name: str, attr_value: Any):
    """装饰器函数，为函数添加属性"""

    def decorator(func):
        setattr(func, attr_name, attr_value)
        return func

    return decorator


def generate_text_hash(text: str) -> str:
    """生成文本哈希值"""

    # 避免空字符串导致计算错误
    text = str(text) + "None"

    # 使用SHA3_256计算文本哈希值
    return sha3_256(text.encode()).hexdigest()
