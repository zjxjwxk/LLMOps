#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/8/28 21:47
@File   :   function_call_agent.py
"""
import json
from typing import Literal

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, RemoveMessage, ToolMessage
from langgraph.constants import END
from langgraph.graph.state import CompiledStateGraph, StateGraph

from internal.core.agent.agents.base_agent import BaseAgent
from internal.core.agent.entities.agent_entity import AgentState, AGENT_SYSTEM_PROMPT_TEMPLATE
from internal.exception import FailException


class FunctionCallAgent(BaseAgent):
    """基于函数/工具调用的Agent"""

    def run(self, query: str, history: list[AnyMessage] = None, long_term_memory: str = ""):
        """运行Agent应用"""

        if history is None:
            history = []

        # 构建Agent
        agent = self._build_graph()

        # 调用Agent
        return agent.invoke({
            "messages": [HumanMessage(content=query)],
            "history": history,
            "long_term_memory": long_term_memory
        })

    def _build_graph(self) -> CompiledStateGraph:
        """构建LangGraph图结构编译程序"""

        # 创建图
        graph = StateGraph(AgentState)

        # 添加节点
        graph.add_node("long_term_memory_recall", self._long_term_memory_recall_node)
        graph.add_node("llm", self._llm_node)
        graph.add_node("tools", self._tools_node)

        # 添加边、起点和终点
        graph.set_entry_point("long_term_memory_recall")
        graph.add_edge("long_term_memory_recall", "llm")
        graph.add_conditional_edges("llm", self._tools_condition)
        graph.add_edge("tools", "llm")

        # 编译应用并返回
        agent = graph.compile()
        return agent

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        """长期记忆召回节点"""

        # 获取长期记忆
        long_term_memory = ""
        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]

        # 构建预设消息列表
        preset_messages = [
            SystemMessage(AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                preset_prompt=self.agent_config.preset_prompt,
                long_term_memory=long_term_memory
            ))
        ]

        # 获取短期记忆
        history = state["history"]
        if isinstance(history, list) and len(history) > 0:
            # 校验是否为消息对（偶数）
            if len(history) % 2 != 0:
                raise FailException("智能体历史消息列表格式错误")
            # 添加短期记忆
            preset_messages.extend(history)

        # 添加人类消息
        human_message = state["messages"][-1]
        preset_messages.append(HumanMessage(human_message.content))

        # 将State中的人类消息替换为预设消息+人类消息
        return {"messages": [RemoveMessage(id=human_message.id), *preset_messages]}

    def _llm_node(self, state: AgentState) -> AgentState:
        """LLM节点"""

        # 获取LLM
        llm = self.agent_config.llm

        # 检测是否支持/需要绑定工具
        if hasattr(llm, "bind_tools") and callable(getattr(llm, "bind_tools")) and len(self.agent_config.tools) > 0:
            llm.bind_tools(self.agent_config.tools)

        # 流式调用LLM
        gathered = None
        is_first_chunk = True
        for chunk in llm.stream(state["messages"]):
            if is_first_chunk:
                gathered = chunk
                is_first_chunk = False
            else:
                gathered += chunk

        return {"messages": [gathered]}

    def _tools_node(self, state: AgentState) -> AgentState:
        """工具执行节点"""

        # 构建工具字典
        tools_by_name = {tool.name: tool for tool in self.agent_config.tools}

        # 获取AI消息中的工具调用参数
        tool_calls = state["messages"][-1].tool_calls

        messages = []
        for tool_call in tool_calls:
            # 调用对应工具
            tool = tools_by_name[tool_call["name"]]
            tool_result = tool.invoke(tool_call["args"])

            # 添加工具消息
            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=json.dumps(tool_result),
                name=tool_call["name"],
            ))

        return {"messages": messages}

    @classmethod
    def _tools_condition(cls, state: AgentState) -> Literal["tools", "__end__"]:
        """判断是需要工具调用，还是直接结束"""

        # 提取最后一条消息
        messages = state["messages"]
        ai_message = messages[-1]

        # 判断是否需要工具调用
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"

        return END
