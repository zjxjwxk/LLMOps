#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话服务

@Author :   Xinkang Wu
@Time   :   2026/8/23 23:00
@File   :   conversation_service.py
"""
import logging
from dataclasses import dataclass

from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from internal.entity.conversation_entity import SUMMARIZER_TEMPLATE, CONVERSATION_NAME_TEMPLATE, ConversationInfo, \
    SuggestedQuestions, SUGGESTED_QUESTIONS_TEMPLATE
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class ConversationService(BaseService):
    """对话服务"""

    db: SQLAlchemy

    @classmethod
    def summary(cls, human_message: str, ai_message: str, old_summary: str = "") -> str:
        """总结新的摘要（根据人类消息、AI消息和老摘要）"""

        # 构建Prompt
        prompt = ChatPromptTemplate.from_template(SUMMARIZER_TEMPLATE)

        # 构建LLM
        llm = ChatOpenAI(temperature=0.5)

        # 构建链
        summary_chain = prompt | llm | StrOutputParser()

        # 调用链
        new_summary = summary_chain.invoke({
            "summary": old_summary,
            "new_lines": f"Human: {human_message}\nAI: {ai_message}",
        })

        return new_summary

    @classmethod
    def generate_conversation_name(cls, query: str) -> str:
        """生成对话名称"""

        # 构建Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", CONVERSATION_NAME_TEMPLATE),
            ("human", "{query}")
        ])

        # 构建LLM
        llm = ChatOpenAI(temperature=0)
        structured_llm = llm.with_structured_output(ConversationInfo)  # 结构化输出，其中利用 Chain of thought 思维链提升回答准确度

        # 构建链
        chain = prompt | structured_llm

        # 截断过长对话
        if len(query) > 2000:
            query = query[:300] + "...[TRUNCATED]..." + query[-300:]
        query = query.replace("\n", " ")

        # 调用链
        conversation_info = chain.invoke({"query": query})

        # 提取对话名称
        name = "新的对话"
        try:
            if conversation_info and hasattr(conversation_info, "subject"):
                name = conversation_info.subject
        except Exception as e:
            logging.exception(f"生成对话名称失败，conversation_info：{conversation_info}，错误信息：{str(e)}")

        # 截断过长名称
        if len(name) > 75:
            name = name[:75] + "..."

        return name

    @classmethod
    def generate_suggested_questions(cls, histories: str) -> list[str]:
        """生成建议问题（根据历史消息，生成最多3个建议问题）"""

        # 构建Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", SUGGESTED_QUESTIONS_TEMPLATE),
            ("human", "{histories}")
        ])

        # 构建LLM
        llm = ChatOpenAI(temperature=0)
        structured_llm = llm.with_structured_output(SuggestedQuestions,
                                                    method="json_schema")

        # 构建链
        chain = prompt | structured_llm

        # 调用链
        suggested_questions = chain.invoke({"histories": histories})

        # 提取建议问题列表
        questions = []
        try:
            if suggested_questions and hasattr(suggested_questions, "questions"):
                questions = suggested_questions.questions
        except Exception as e:
            logging.exception(f"生成建议问题失败，suggested_questions：{suggested_questions}，错误信息：{str(e)}")

        # 去除多余问题
        if len(questions) > 3:
            questions = questions[:3]

        return questions
