#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本嵌入服务

@Author :   Xinkang Wu
@Time   :   2026/7/27 21:44
@File   :   embeddings_service.py
"""
import os
from dataclasses import dataclass, field

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

    # 类变量（共享的模型数据）
    _shared_store: RedisStore = None
    _shared_embeddings: Embeddings = None
    _shared_cache_backed_embeddings: CacheBackedEmbeddings = None
    _initialized: bool = False

    # 实例变量 - 使用 field(default=None) 让 dataclass 不强制要求初始化
    _store: RedisStore = field(default=None, init=False)
    _embeddings: Embeddings = field(default=None, init=False)
    _cache_backed_embeddings: CacheBackedEmbeddings = field(default=None, init=False)

    def __init__(self, redis: Redis):
        """构造函数"""

        if not EmbeddingsService._initialized:
            EmbeddingsService._shared_store = RedisStore(client=redis)

            # 远程Embedding模型
            # EmbeddingsService._shared_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
            # 本地Embedding模型
            EmbeddingsService._shared_embeddings = HuggingFaceEmbeddings(
                model_name="Alibaba-NLP/gte-multilingual-base",
                cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),
                model_kwargs={
                    "trust_remote_code": True,
                    "local_files_only": True,
                },
            )
            EmbeddingsService._shared_cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
                EmbeddingsService._shared_embeddings,
                EmbeddingsService._shared_store,
                namespace="embeddings"
            )
            EmbeddingsService._initialized = True

        # 所有实例共享同一个模型（直接赋值实例属性）
        self._store = EmbeddingsService._shared_store
        self._embeddings = EmbeddingsService._shared_embeddings
        self._cache_backed_embeddings = EmbeddingsService._shared_cache_backed_embeddings

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
