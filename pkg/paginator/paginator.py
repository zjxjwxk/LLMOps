#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用基础分页实体

@Author :   Xinkang Wu
@Time   :   2026/6/30 20:30
@File   :   paginator.py
"""
import math
from dataclasses import dataclass
from typing import Any

from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import Optional, NumberRange

from pkg.sqlalchemy import SQLAlchemy


class PaginatorReq(FlaskForm):
    """通用基础分页请求"""

    current_page = IntegerField("current_page", default=1, validators=[
        Optional(),
        NumberRange(min=1, max=9999, message="页数范围限制为1~9999")
    ])
    page_size = IntegerField("page_size", default=20, validators=[
        Optional(),
        NumberRange(min=1, max=50, message="每页条数限制为1~50")
    ])


@dataclass
class Paginator:
    """分页器"""

    total_page: int = 0  # 总页数
    total_record: int = 0  # 总条数
    current_page: int = 1  # 当前页数
    page_size: int = 20  # 每页条数

    def __init__(self, db: SQLAlchemy, req: PaginatorReq):
        if req is not None:
            self.current_page = req.current_page.data
            self.page_size = req.page_size.data
        self.db = db

    def paginate(self, select) -> list[Any]:
        """执行查询分页"""

        pagination = self.db.paginate(select, page=self.current_page, per_page=self.page_size, error_out=False)

        self.total_record = pagination.total
        self.total_page = math.ceil(pagination.total / self.page_size)

        return pagination.items


@dataclass
class PageModel:
    list: list[Any]
    paginator: Paginator
