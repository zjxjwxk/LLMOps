#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档片段服务

@Author :   Xinkang Wu
@Time   :   2026/8/11 21:54
@File   :   segment_service.py
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import asc

from internal.exception import NotFoundException
from internal.model import Segment, Document
from internal.schema.segment_schema import GetSegmentsWithPageReq
from internal.service import BaseService
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class SegmentService(BaseService):
    """文档片段服务"""

    db: SQLAlchemy

    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID, req: GetSegmentsWithPageReq) -> tuple[
        list[Segment], Paginator]:
        """获取文档片段列表分页"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 获取文档并校验权限
        document = self.get(Document, document_id)
        if document is None or document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise NotFoundException("该知识库文档不存在或当前用户无权访问")

        # 构建分页器
        paginator = Paginator(db=self.db, req=req)

        # 构建筛选器
        filters = [Segment.document_id == document_id]
        if req.search_word.data:
            filters.append(Segment.content.ilike(f"%{req.search_word.data}%"))

        # 执行分页查询
        segments = paginator.paginate(
            self.db.session.query(Segment).filter(*filters).order_by(asc("position"))
        )

        return segments, paginator
