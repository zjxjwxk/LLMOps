#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库常量

@Author :   Xinkang Wu
@Time   :   2026/7/26 16:05
@File   :   dataset_entity.py
"""
from enum import Enum

# 默认知识库描述模版
DEFAULT_DATASET_DESCRIPTION_FORMATTER = "当你需要回答关于{name}的问题时，可以引用该知识库。"


class ProcessType(str, Enum):
    """文档处理类型"""

    AUTOMATIC = "automatic"
    CUSTOM = "custom"


# 默认文档处理规则
DEFAULT_PROCESS_RULE = {
    "mode": "custom",
    "rule": {
        "pre_process_rules": [
            {"id": "remove_extra_space", "enabled": True},
            {"id": "remove_url_and_email", "enabled": True},
        ],
        "segment": {
            "separators": [
                "\n\n",
                "\n",
                "。|！|？",
                "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格\s
                "；|;\s",
                "，|,\s",
                " ",
                ""
            ],
            "chunk_size": 500,
            "chunk_overlap": 50,
        }
    }
}
