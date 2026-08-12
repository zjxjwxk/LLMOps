#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档片段服务

@Author :   Xinkang Wu
@Time   :   2026/8/11 21:54
@File   :   segment_service.py
"""
import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from injector import inject
from redis import Redis
from sqlalchemy import asc

from internal.entity.cache_entity import LOCK_SEGMENT_UPDATE_ENABLED, LOCK_EXPIRE_TIME
from internal.entity.dataset_entity import SegmentStatus
from internal.exception import NotFoundException, FailException
from internal.model import Segment, Document
from internal.schema.segment_schema import GetSegmentsWithPageReq
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .keyword_table_service import KeywordTableService
from .vector_database_service import VectorDatabaseService


@inject
@dataclass
class SegmentService(BaseService):
    """文档片段服务"""

    db: SQLAlchemy
    redis_client: Redis
    vector_database_service: VectorDatabaseService
    keyword_table_service: KeywordTableService

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

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """获取文档片段详情"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 获取文档片段并校验权限
        segment = self.get(Segment, segment_id)
        if (
                segment is None
                or str(segment.account_id) != account_id
                or segment.dataset_id != dataset_id
                or segment.document_id != document_id
        ):
            return NotFoundException("该文档片段不存在或当前用户无权访问")

        return segment

    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID, enabled: bool) -> Segment:
        """更新文档片段启用状态"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 获取文档片段并校验权限
        segment = self.get(Segment, segment_id)
        if (
                segment is None
                or str(segment.account_id) != account_id
                or segment.dataset_id != dataset_id
                or segment.document_id != document_id
        ):
            return NotFoundException("该文档片段不存在或当前用户无权修改")

        # 判断文档片段当前是否可启用（仅构建完成后才可启用）
        if segment.status != SegmentStatus.COMPLETED:
            raise FailException("当前文档片段未构建完成，请稍后重试")

        # 判断文档片段启用状态是否需要更新
        if segment.enabled == enabled:
            raise FailException(f"更新文档片段启用状态错误，当前已为{'启用' if enabled else '禁用'}状态")

        # 获取分布式锁
        cache_key = LOCK_SEGMENT_UPDATE_ENABLED.format(segment_id=segment_id)
        cache_result = self.redis_client.get(cache_key)
        if cache_result is not None:
            raise FailException("当前文档片段正在更新启用状态，请稍后重试")

        with self.redis_client.lock(cache_key, LOCK_EXPIRE_TIME):
            try:
                # 更新文档片段启用状态至DB
                self.update(
                    segment,
                    enabled=enabled,
                    disabled_at=None if enabled else datetime.now(),
                )

                # 更新知识库的关键词表
                document = segment.document
                if enabled is True and document.enabled is True:
                    # 启用片段，则新增关键词中的片段
                    self.keyword_table_service.add_keyword_table_from_segment_ids(dataset_id, [segment_id])
                else:
                    # 禁用片段，则删除关键词中的片段
                    self.keyword_table_service.delete_keyword_table_from_segment_ids(dataset_id, [segment_id])

                # 更新文档片段启用状态至向量数据库
                self.vector_database_service.collection.data.update(
                    uuid=segment.node_id,
                    properties={"segment_enabled": enabled},
                )
            except Exception as e:
                logging.exception(f"更新文档片段启用状态失败，文档片段ID：{segment_id}，错误信息：{str(e)}")
                self.update(
                    segment,
                    error=str(e),
                    status=SegmentStatus.ERROR,
                    enabled=False,
                    disabled_at=datetime.now(),
                    stopped_at=datetime.now()
                )
                raise FailException("更新文档片段启用状态失败，请稍后重试")
