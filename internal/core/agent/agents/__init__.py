#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/8/28 21:27
@File   :   __init__.py
"""
from .base_agent import BaseAgent
from .function_call_agent import FunctionCallAgent

__all__ = ["BaseAgent", "FunctionCallAgent"]
