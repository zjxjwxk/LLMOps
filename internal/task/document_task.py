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
    """更新文档启用状态"""

    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.update_document_enabled(document_id)
