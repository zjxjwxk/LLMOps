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

from flask import request
from injector import inject

from internal.schema.document_schema import CreateDocumentsReq, CreateDocumentsResp, GetDocumentResp, \
    UpdateDocumentNameReq, GetDocumentsWithPageReq, GetDocumentsWithPageResp
from internal.service import DocumentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message


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

    def update_document_name(self, dataset_id: UUID, document_id: UUID):
        """更新文档名称"""

        # 提取请求并校验
        req = UpdateDocumentNameReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务更新文档名称
        self.document_service.update_document(dataset_id, document_id, name=req.name.data)

        return success_message("更新文档名称成功")

    def get_document(self, dataset_id: UUID, document_id: UUID):
        """获取文档详情"""

        # 调用服务查询文档详情
        document = self.document_service.get_document(dataset_id, document_id)

        resp = GetDocumentResp()
        return success_json(resp.dump(document))

    def get_documents_with_page(self, dataset_id: UUID):
        """获取文档列表分页"""

        # 提取请求并校验
        req = GetDocumentsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务获取文档列表分页
        documents, paginator = self.document_service.get_documents_with_page(dataset_id, req)

        resp = GetDocumentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(documents), paginator=paginator))

    def get_documents_status(self, dataset_id: UUID, batch: str):
        """获取文档列表状态（根据知识库和批次）"""

        documents_status = self.document_service.get_documents_status(dataset_id, batch)
        return success_json(documents_status)
