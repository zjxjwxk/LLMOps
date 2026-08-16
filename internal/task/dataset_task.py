#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库异步任务

@Author :   Xinkang Wu
@Time   :   2026/8/16 20:22
@File   :   dataset_task.py
"""
from uuid import UUID

from celery import shared_task


@shared_task
def delete_dataset(dataset_id: UUID) -> None:
    """删除知识库后续操作：删除文档记录、片段记录、关键词表记录、知识库查询记录、向量数据库数据"""

    from app.http.module import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)
