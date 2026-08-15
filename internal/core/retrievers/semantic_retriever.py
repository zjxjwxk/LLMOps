#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向量检索器

@Author :   Xinkang Wu
@Time   :   2026/8/15 15:24
@File   :   semantic_retriever.py
"""
from uuid import UUID

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document as LangChainDocument
from langchain_core.retrievers import BaseRetriever
from langchain_weaviate import WeaviateVectorStore
from pydantic import Field
from weaviate.classes.query import Filter


class SemanticRetriever(BaseRetriever):
    """向量检索器"""

    dataset_ids: list[UUID]
    vector_store: WeaviateVectorStore
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[
        LangChainDocument]:
        """相似性搜索"""

        k = self.search_kwargs.pop("k", 4)

        # 执行相似性搜索
        search_result = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            **{
                "filters": Filter.all_of([
                    Filter.by_property("dataset_id").contains_any([str(dataset_id) for dataset_id in self.dataset_ids]),
                    Filter.by_property("document_enabled").equal(True),
                    Filter.by_property("segment_enabled").equal(True)
                ]),
                **self.search_kwargs,
            }
        )

        if search_result is None or len(search_result) == 0:
            return []

        langchain_documents, scores = zip(*search_result)

        # 为文档添加分数元数据
        for langchain_document, score in zip(langchain_documents, scores):
            langchain_document.metadata["score"] = score

        return list(langchain_documents)
