#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向量数据库服务

@Author :   Xinkang Wu
@Time   :   2026/5/4 20:41
@File   :   vector_database_service.py
"""
import os

import weaviate
from injector import inject
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate.client import WeaviateClient

from .embeddings_service import EmbeddingsService


@inject
class VectorDatabaseService:
    """向量数据库服务"""

    client: WeaviateClient
    vector_store: WeaviateVectorStore
    embeddings_service: EmbeddingsService

    def __init__(self, embeddings_service: EmbeddingsService):
        self.embeddings_service = embeddings_service

        # 创建并连接Weaviate向量数据库
        self.client = weaviate.connect_to_local(
            host=os.getenv("WEAVIATE_HOST"),
            port=int(os.getenv("WEAVIATE_PORT")),
        )

        # 创建LangChain向量数据库
        self.vector_store = WeaviateVectorStore(
            self.client,
            index_name="Dataset",
            text_key="text",
            embedding=self.embeddings_service.embeddings
        )

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器"""
        return self.vector_store.as_retriever()

    @classmethod
    def combine_documents(cls, documents: list[Document]) -> str:
        """将文档列表使用换行符进行合并"""
        return "\n\n".join([document.page_content for document in documents])
