#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全文检索器

@Author :   Xinkang Wu
@Time   :   2026/8/15 16:21
@File   :   full_text_retriever.py
"""
from collections import Counter
from uuid import UUID

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document as LangChainDocument
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from internal.model import KeywordTable, Segment
from internal.service import JiebaService
from pkg.sqlalchemy import SQLAlchemy


class FullTextRetriever(BaseRetriever):
    """全文检索器"""

    db: SQLAlchemy
    dataset_ids: list[UUID]
    jieba_service: JiebaService
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[
        LangChainDocument]:
        """关键词检索"""

        # 提取查询语句的关键词列表
        keywords = self.jieba_service.extract_keywords(query)

        # 查询知识库的关键词表
        keyword_table_records = self.db.session.query(KeywordTable).with_entities(KeywordTable.keyword_table).filter(
            KeywordTable.dataset_id.in_(self.dataset_ids)
        ).all()
        keyword_tables = [keyword_table_record.keyword_table for keyword_table_record in keyword_table_records]

        # 找出匹配查询语句关键词列表的片段ID列表
        match_segment_ids = []
        for keyword_table in keyword_tables:
            for keyword, segment_ids in keyword_table.items():
                if keyword in keywords:
                    match_segment_ids.extend(segment_ids)

        # 统计片段ID的出现次数
        segment_id_counter = Counter(match_segment_ids)

        # 获取频率最高的k个片段
        k = self.search_kwargs.get("k", 4)
        top_k_segment_ids = segment_id_counter.most_common(k)

        # 查询片段列表信息
        segments = self.db.session.query(Segment).filter(
            Segment.id.in_([segment_id for segment_id, _ in top_k_segment_ids])
        ).all()

        segment_dict = {
            str(segment.id): segment for segment in segments
        }

        # 根据频率对top k个片段进行排序
        sorted_segments = [segment_dict[str(segment_id)] for segment_id, freq in top_k_segment_ids if
                           segment_id in segment_dict]

        # 构建为LangChain文档列表
        langchain_documents = [LangChainDocument(
            page_content=segment.content,
            metadata={
                "account_id": str(segment.account_id),
                "dataset_id": str(segment.dataset_id),
                "document_id": str(segment.document_id),
                "segment_id": str(segment.id),
                "node_id": str(segment.node_id),
                "document_enabled": True,
                "segment_enabled": True,
                "score": 0
            }
        ) for segment in sorted_segments]

        return langchain_documents
