#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本嵌入服务

@Author :   Xinkang Wu
@Time   :   2026/7/27 21:44
@File   :   embeddings_service.py
"""
import os
from dataclasses import dataclass

import tiktoken
from injector import inject
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from redis import Redis


@inject
@dataclass
class EmbeddingsService:
    """文本嵌入服务"""

    _store: RedisStore
    _embeddings: Embeddings
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self, redis: Redis):
        """构造函数"""

        self._store = RedisStore(client=redis)
        # 远程Embedding模型
        # self._embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        # 本地Embedding模型
        self._embeddings = HuggingFaceEmbeddings(
            model_name="Alibaba-NLP/gte-multilingual-base",
            cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),
            model_kwargs={
                "trust_remote_code": True,
                "local_files_only": True,
            },
        )
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,
            namespace="embeddings"
        )

    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算文本token数"""

        encoding = tiktoken.encoding_for_model("text-embedding-3-large")
        return len(encoding.encode(query))

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings
