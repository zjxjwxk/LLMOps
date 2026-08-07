#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档处理器

@Author :   Xinkang Wu
@Time   :   2026/7/31 16:47
@File   :   document_handler.py
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject

from internal.schema.document_schema import CreateDocumentsReq, CreateDocumentsResp
from internal.service import DocumentService
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class DocumentHandler:
    """文档处理器"""

    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        """创建文档列表"""

        req = CreateDocumentsReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务创建文档列表，返回文档列表信息和处理批次
        documents, batch = self.document_service.create_documents(dataset_id, **req.data)

        resp = CreateDocumentsResp()
        return success_json(resp.dump((documents, batch)))

    def get_documents_status(self, dataset_id: UUID, batch: str):
        """获取文档列表状态（根据知识库和批次）"""

        documents_status = self.document_service.get_documents_status(dataset_id, batch)
        return success_json(documents_status)
