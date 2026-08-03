#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档服务

@Author :   Xinkang Wu
@Time   :   2026/7/31 17:22
@File   :   document_service.py
"""
import logging
import random
import time
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc

from internal.entity.dataset_entity import ProcessType
from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION
from internal.exception import ForbiddenException, FailException
from internal.model import Document, Dataset, UploadFile, ProcessRule
from internal.service import BaseService
from internal.task.document_task import build_documents
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class DocumentService(BaseService):
    """文档服务"""

    db: SQLAlchemy

    def create_documents(
            self,
            dataset_id: UUID,
            upload_file_ids: list[UUID],
            process_type: str = ProcessType.AUTOMATIC,
            rule: dict = None
    ) -> tuple[list[Document], str]:
        """创建文档列表，并调用异步任务"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 校验知识库权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException("该知识库不存在或当前用户无权访问")

        # 提取文件并校验文件权限和扩展名
        upload_files = self.db.session.query(UploadFile).filter(
            UploadFile.account_id == account_id,
            UploadFile.id.in_(upload_file_ids)
        ).all()

        upload_files = [upload_file for upload_file in upload_files
                        if upload_file.extension.lower() in ALLOWED_DOCUMENT_EXTENSION]

        if len(upload_files) == 0:
            logging.warning(
                f"上传文档列表时，未找到任何合法文件，account_id: {account_id}, dataset_id: {dataset_id}, upload_file_ids: {upload_file_ids}")
            raise FailException("未找到任何合法文件，请重新上传")

        # 创建批次与处理规则
        batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
        process_rule = self.create(
            ProcessRule,
            account_id=account_id,
            dataset_id=dataset_id,
            mode=process_type,
            rule=rule,
        )

        # 获取知识库的最新文档位置
        position = self.get_latest_document_position(dataset_id)

        # 创建文档列表记录
        documents = []
        for upload_file in upload_files:
            position += 1
            document = self.create(
                Document,
                account_id=account_id,
                dataset_id=dataset_id,
                upload_file_id=upload_file.id,
                process_rule_id=process_rule.id,
                batch=batch,
                name=upload_file.name,
                position=position,
            )
            documents.append(document)

        # TODO: 调用异步任务，存储至向量数据库
        build_documents.delay([document.id for document in documents])

        return documents, batch

    def get_latest_document_position(self, dataset_id: UUID) -> int:
        """获取知识库的最新文档位置"""

        document = self.db.session.query(Document).filter(
            Document.dataset_id == dataset_id,
        ).order_by(desc("position")).first()

        return document.position if document else 0
