#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/23 16:38
@File   :   config.py
"""


class Config:
    def __init__(self):
        # 关闭Flask-WTF的CSRF保护
        self.WTF_CSRF_ENABLED = False
