#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/23 16:25
@File   :   app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class CompletionReq(FlaskForm):
    """基础聊天接口请求验证"""

    # 必填、长度最大为2000
    query = StringField("query", validators=[
        DataRequired(message="用户提问不能为空"),
        Length(max=2000, message="用户提问长度不能超过2000"),
    ])
