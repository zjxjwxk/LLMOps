#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档异步任务

@Author :   Xinkang Wu
@Time   :   2026/8/1 17:34
@File   :   document_task.py
"""
from uuid import UUID

from celery import shared_task


@shared_task
def build_documents(document_ids: list[UUID]) -> None:
    """构建文档列表"""

    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.build_documents(document_ids)


@shared_task
def update_document_enabled(document_id: UUID) -> None:
    """更新文档启用状态至向量数据库"""

    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.update_document_enabled(document_id)


@shared_task
def delete_document(dataset_id: UUID, document_id: UUID) -> None:
    """删除文档后续操作：删除文档片段、更新关键词表、删除向量数据库记录"""

    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_document(dataset_id, document_id)
