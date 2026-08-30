#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/8/29 16:47
@File   :   agent_queue_manager.py
"""
import queue
import time
import uuid
from queue import Queue
from typing import Generator
from uuid import UUID

from redis import Redis

from internal.core.agent.entities.queue_entity import AgentQueueEvent, QueueEvent
from internal.entity.conversation_entity import InvokeFrom


class AgentQueueManager:
    """Agent事件队列管理器"""

    queue: Queue
    user_id: UUID
    task_id: UUID
    invoke_from: InvokeFrom
    redis_client: Redis

    def __init__(
            self,
            user_id: UUID,
            task_id: UUID,
            invoke_from: InvokeFrom,
            redis_client: Redis
    ) -> None:
        """构造函数"""

        # 初始化
        self.queue = Queue()
        self.user_id = user_id
        self.task_id = task_id
        self.invoke_from = invoke_from
        self.redis_client = redis_client

        # 根据用户类型生成缓存键
        user_prefix = "account" if invoke_from in [InvokeFrom.WEB_APP, InvokeFrom.DEBUGGER] else "end-user"

        # 构建任务缓存键，标识任务已启动
        self.redis_client.setex(
            self.generate_task_running_cache_key(task_id),
            1800,
            f"{user_prefix}-{str(user_id)}"
        )

    def listen(self) -> Generator:
        """监听队列返回的流式数据"""

        listen_timeout = 600
        start_time = time.time()
        last_ping_time = 0

        # 死循环获取队列数据
        while True:
            try:
                # 获取队列中的事件并返回
                item = self.queue.get(timeout=1)
                if item is None:
                    break
                yield item
            except queue.Empty:
                # 队列为空，继续尝试获取
                continue
            finally:
                # 每次获取事件后

                # 更新总耗时
                elapsed_time = time.time() - start_time

                # 每10秒发起一个PING请求事件
                if elapsed_time // 10 > last_ping_time:
                    # 添加PING连通事件
                    self.publish(AgentQueueEvent(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.PING
                    ))
                    last_ping_time = elapsed_time // 10

                # 判断总耗时是否超时
                if elapsed_time >= listen_timeout:
                    # 添加超时事件
                    self.publish(AgentQueueEvent(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.TIMEOUT
                    ))

                # 判断是否停止
                if self._is_stopped():
                    # 添加停止事件
                    self.publish(AgentQueueEvent(
                        id=uuid.uuid4(),
                        task_id=self.task_id,
                        event=QueueEvent.STOP
                    ))

    def stop_listen(self) -> None:
        """停止监听队列"""

        self.queue.put(None)

    def publish(self, agent_queue_event: AgentQueueEvent):
        """发布事件至队列"""

        self.queue.put(agent_queue_event)

        # 判断是否为停止事件
        if agent_queue_event.event in [QueueEvent.STOP, QueueEvent.ERROR, QueueEvent.TIMEOUT, QueueEvent.AGENT_END]:
            self.stop_listen()

    def publish_error(self, error) -> None:
        """发布错误事件至队列"""

        self.publish(AgentQueueEvent(
            id=uuid.uuid4(),
            task_id=self.task_id,
            event=QueueEvent.ERROR,
            observation=str(error)
        ))

    def _is_stopped(self) -> bool:
        """判断任务是否停止"""

        task_stopped_cache_key = self.generate_task_stopped_cache_key(self.task_id)
        result = self.redis_client.get(task_stopped_cache_key)

        return result is not None

    @classmethod
    def generate_task_running_cache_key(cls, task_id: UUID) -> str:
        """生成任务已启动缓存键"""

        return f"generate_task_running:{str(task_id)}"

    @classmethod
    def generate_task_stopped_cache_key(cls, task_id: UUID) -> str:
        """生成任务已停止缓存键"""

        return f"generate_task_stopped:{str(task_id)}"
