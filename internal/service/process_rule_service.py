#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档处理规则服务

@Author :   Xinkang Wu
@Time   :   2026/8/2 15:43
@File   :   process_rule_service.py
"""
import re
from dataclasses import dataclass
from typing import Callable

from injector import inject
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter

from internal.model import ProcessRule


@inject
@dataclass
class ProcessRuleService:
    """文档处理规则服务"""

    @classmethod
    def get_text_splitter_by_process_rule(
            cls,
            process_rule: ProcessRule,
            length_function: Callable[[str], int] = len,
            **kwargs
    ) -> TextSplitter:
        """根据文档处理规则和长度计算函数，获取文本分割器"""

        return RecursiveCharacterTextSplitter(
            chunk_size=process_rule.rule["segment"]["chunk_size"],
            chunk_overlap=process_rule.rule["segment"]["chunk_overlap"],
            separators=process_rule.rule["segment"]["separators"],
            is_separator_regex=True,
            length_function=length_function,
            **kwargs
        )

    @classmethod
    def clean_text_by_process_rule(cls, text: str, process_rule: ProcessRule) -> str:
        """根据文档处理规则，清除文本中的多余字符串"""

        for pre_process_rule in process_rule.rule["pre_process_rules"]:
            # 删除多余空格
            if pre_process_rule["id"] == "remove_extra_space" and pre_process_rule["enabled"] is True:
                # 多个换行符=>两个换行符
                pattern = r'\n{3,}'
                text = re.sub(pattern, '\n\n', text)
                # 多个空格=>单个空格
                pattern = r'[\t\f\r\x20\u00a0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000]{2,}'
                text = re.sub(pattern, ' ', text)
            # 删除URL链接和邮箱
            if pre_process_rule["id"] == "remove_url_and_email" and pre_process_rule["enabled"] is True:
                # 删除邮箱
                pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
                text = re.sub(pattern, '', text)
                # 删除URL链接
                pattern = r'https?://[^\s]+'
                text = re.sub(pattern, '', text)

        return text
