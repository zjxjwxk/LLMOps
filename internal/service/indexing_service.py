#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索引构建服务

@Author :   Xinkang Wu
@Time   :   2026/8/1 17:40
@File   :   indexing_service.py
"""
import logging
import re
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from flask import Flask, current_app
from injector import inject
from langchain_core.documents import Document as LangChainDocument
from sqlalchemy import func

from internal.core.file_extractor import FileExtractor
from internal.entity.dataset_entity import DocumentStatus, SegmentStatus
from internal.lib.helper import generate_text_hash
from internal.model import Document, Segment
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService
from .embeddings_service import EmbeddingsService
from .jieba_service import JiebaService
from .keyword_table_service import KeywordTableService
from .process_rule_service import ProcessRuleService
from .vector_database_service import VectorDatabaseService


@inject
@dataclass
class IndexingService(BaseService):
    """索引构建服务"""

    db: SQLAlchemy
    file_extractor: FileExtractor
    process_rule_service: ProcessRuleService
    embedding_service: EmbeddingsService
    jieba_service: JiebaService
    keyword_table_service: KeywordTableService
    vector_database_service: VectorDatabaseService

    def build_documents(self, document_ids: list[UUID]) -> None:
        """构建知识库文档列表索引，包括加载、分割、索引、存储"""

        # 获取文档列表
        documents = self.db.session.query(Document).filter(
            Document.id.in_(document_ids)
        ).all()

        # 构建文档
        for document in documents:
            try:
                # 更新状态为解析中，并记录解析开始时间
                self.update(document, status=DocumentStatus.PARSING, processing_started_at=datetime.now())

                # 解析文档实体为LangChain文档列表，并更新文档状态、字符总数、解析完成时间
                langchain_documents = self._parsing(document)

                # 分割LangChain文档列表，并更新文档状态、token总数、分割完成时间
                langchain_segments = self._splitting(document, langchain_documents)

                self._indexing(document, langchain_segments)

                self._completed(document, langchain_segments)

            except Exception as e:
                logging.exception(f"构建文档错误：{str(e)}")
                self.update(
                    document,
                    status=DocumentStatus.ERROR,
                    error=str(e),
                    stopped_at=datetime.now(),
                )

    def _parsing(self, document: Document) -> list[LangChainDocument]:
        """解析文档实体为LangChain文档列表"""

        # 获取文档的文件实体，并加载为LangChain文档列表
        upload_file = document.upload_file
        langchain_documents = self.file_extractor.load(upload_file, False, True)

        # 清除文本中的多余字符
        for langchain_document in langchain_documents:
            langchain_document.page_content = self._clean_extra_text(langchain_document.page_content)

        # 更新文档状态、字符总数、解析完成时间
        self.update(
            document,
            character_count=sum([len(langchain_document.page_content) for langchain_document in langchain_documents]),
            status=DocumentStatus.SPLITTING,
            parsing_completed_at=datetime.now()
        )

        return langchain_documents

    def _splitting(self, document: Document, langchain_documents: list[LangChainDocument]) -> list[LangChainDocument]:
        """分割LangChain文档列表"""

        # 获取文档处理规则
        process_rule = document.process_rule

        # 获取文本分割器
        text_splitter = self.process_rule_service.get_text_splitter_by_process_rule(
            process_rule,
            self.embedding_service.calculate_token_count
        )

        # 清除多余字符串
        for langchain_document in langchain_documents:
            langchain_document.page_content = self.process_rule_service.clean_text_by_process_rule(
                langchain_document.page_content,
                process_rule
            )

        # 分割LangChain文档列表
        langchain_segments = text_splitter.split_documents(langchain_documents)

        # 获取文档实体的最大片段位置
        position = self.db.session.query(func.coalesce(func.max(Segment.position), 0)).filter(
            Segment.document_id == document.id
        ).scalar()

        # 存储片段实体并添加向量数据库元数据
        segments = []
        for langchain_segment in langchain_segments:
            position += 1
            content = langchain_segment.page_content
            segment = self.create(
                Segment,
                account_id=document.account_id,
                dataset_id=document.dataset_id,
                document_id=document.id,
                node_id=uuid.uuid4(),
                position=position,
                content=content,
                character_count=len(content),
                token_count=self.embedding_service.calculate_token_count(content),
                hash=generate_text_hash(content),
                status=SegmentStatus.WAITING
            )
            langchain_segment.metadata = {
                "account_id": str(document.account_id),
                "dataset_id": str(document.dataset_id),
                "document_id": str(document.id),
                "segment_id": str(segment.id),
                "node_id": str(segment.node_id),
                "document_enabled": False,
                "segment_enabled": False,
            }
            segments.append(segment)

        # 更新文档状态、token总数、分割完成时间
        self.update(
            document,
            token_count=sum([segment.token_count for segment in segments]),
            status=DocumentStatus.INDEXING,
            splitting_completed_at=datetime.now()
        )

        return langchain_segments

    def _indexing(self, document: Document, langchain_segments: list[LangChainDocument]) -> None:
        """构建文档索引，包括关键词提取、关键词表构建"""

        for langchain_segment in langchain_segments:
            # 提取片段关键词，数量最多10个
            keywords = self.jieba_service.extract_keywords(langchain_segment.page_content, 10)

            # 更新片段关键词
            self.db.session.query(Segment).filter(
                Segment.id == langchain_segment.metadata["segment_id"]
            ).update({
                "keywords": keywords,
                "status": SegmentStatus.INDEXING,
                "indexing_completed_at": datetime.now()
            })

            # 获取知识库的关键词表
            keyword_table_record = self.keyword_table_service.get_keyword_table_from_dataset_id(document.dataset_id)
            keyword_table = {
                field: set(value) for field, value in keyword_table_record.keyword_table.items()
            }

            # 将新关键词添加到关键词表中
            for keyword in keywords:
                if keyword not in keyword_table:
                    keyword_table[keyword] = set()
                keyword_table[keyword].add(langchain_segment.metadata["segment_id"])

            # 更新关键词表
            self.update(
                keyword_table_record,
                keyword_table={field: list(value) for field, value in keyword_table.items()}
            )

        # 更新文档索引完成时间
        self.update(
            document,
            indexing_completed_at=datetime.now()
        )

    def _completed(self, document: Document, langchain_segments: list[LangChainDocument]) -> None:
        """存储文档片段到向量数据库，并更新文档状态"""

        # 更新向量数据库元数据中，文档和片段的启用状态
        for langchain_segment in langchain_segments:
            langchain_segment.metadata["document_enabled"] = True
            langchain_segment.metadata["segment_enabled"] = True

        # 批量更新片段状态、完成时间、启用状态
        def thread_func(flask_app: Flask, chunks: list[LangChainDocument], ids: list[UUID]) -> None:
            """线程函数，执行向量数据库存储和DB存储"""

            with flask_app.app_context():
                self.vector_database_service.vector_store.add_documents(chunks, ids=ids)

                with self.db.auto_commit():
                    self.db.session.query(Segment).filter(
                        Segment.node_id.in_(ids)
                    ).update({
                        "status": SegmentStatus.COMPLETED,
                        "completed_at": datetime.now(),
                        "enabled": True
                    })

        # 创建线程池（线程数为5）
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            # 批量存储片段至向量数据库，每批最多存储10条
            for i in range(0, len(langchain_segments), 10):
                # 提取片段列表和node_id列表
                chunks = langchain_segments[i:i + 10]
                ids = [chunk.metadata["node_id"] for chunk in chunks]

                # 提交线程任务
                futures.append(executor.submit(thread_func, current_app._get_current_object(), chunks, ids))

            # 等待所有线程执行结束
            for future in futures:
                future.result()

        # 更新文档状态、完成时间、启用状态
        self.update(
            document,
            status=DocumentStatus.COMPLETED,
            completed_at=datetime.now(),
            enabled=True
        )

    @classmethod
    def _clean_extra_text(cls, text: str) -> str:
        """清除文本中的多余字符"""

        text = re.sub(r'<\|', '<', text)
        text = re.sub(r'\|>', '>', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\xEF\xBF\xBE]', '', text)
        text = re.sub('\uFFFE', '', text)  # 删除零宽非标记字符
        return text
