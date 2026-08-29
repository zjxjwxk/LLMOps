#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础Agent

@Author :   Xinkang Wu
@Time   :   2026/8/28 21:28
@File   :   base_agent.py
"""
from abc import ABC, abstractmethod

from langchain_core.messages import AnyMessage

from internal.core.agent.entities.agent_entity import AgentConfig


class BaseAgent(ABC):
    """基础Agent"""

    # Agent配置
    agent_config: AgentConfig

    def __init__(self, agent_config: AgentConfig):
        """构造函数，初始化Agent配置"""
        self.agent_config = agent_config

    @abstractmethod
    def run(
            self,
            query: str,
            history: list[AnyMessage] = None,
            long_term_memory: str = "",
    ):
        """Agent执行函数"""
        raise NotImplementedError("Agent智能体run函数未实现")
