#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
结巴分词服务

@Author :   Xinkang Wu
@Time   :   2026/7/28 20:58
@File   :   jieba_service.py
"""
from dataclasses import dataclass

import jieba.analyse
from injector import inject
from jieba.analyse import default_tfidf

from internal.entity.jieba_entity import STOPWORD_SET


@inject
@dataclass
class JiebaService:
    """结巴分词服务"""

    def __init__(self):
        """构造函数"""

        default_tfidf.stop_words = STOPWORD_SET

    @classmethod
    def extract_keywords(cls, text: str, max_keyword_pre_chunk: int = 10) -> list[str]:
        """提取文本关键词列表"""

        return jieba.analyse.extract_tags(
            sentence=text,
            topK=max_keyword_pre_chunk,
        )
