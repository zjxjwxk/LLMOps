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

from internal.core.agent.agents.agent_queue_manager import AgentQueueManager
from internal.core.agent.entities.agent_entity import AgentConfig


class BaseAgent(ABC):
    """基础Agent"""

    # Agent配置
    agent_config: AgentConfig
    # Agent事件队列管理器
    agent_queue_manager: AgentQueueManager

    def __init__(
            self,
            agent_config: AgentConfig,
            agent_queue_manager: AgentQueueManager
    ):
        """构造函数"""

        self.agent_config = agent_config
        self.agent_queue_manager = agent_queue_manager

    @abstractmethod
    def run(
            self,
            query: str,  # 用户提问
            history: list[AnyMessage] = None,  # 短期记忆
            long_term_memory: str = "",  # 长期记忆
    ):
        """Agent执行函数"""
        raise NotImplementedError("Agent智能体run函数未实现")
