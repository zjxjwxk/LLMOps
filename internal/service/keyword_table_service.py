#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关键词表服务

@Author :   Xinkang Wu
@Time   :   2026/8/2 17:29
@File   :   keyword_table_service.py
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.model import KeywordTable
from internal.service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class KeywordTableService(BaseService):
    """关键词表服务"""

    db: SQLAlchemy

    def get_keyword_table_from_dataset_id(self, dataset_id: UUID) -> KeywordTable:
        """获取知识库的关键词表"""

        keyword_table = self.db.session.query(KeywordTable).filter(
            KeywordTable.dataset_id == dataset_id,
        ).one_or_none()

        if keyword_table is None:
            keyword_table = self.create(KeywordTable, dataset_id=dataset_id, keyword_table={})

        return keyword_table
