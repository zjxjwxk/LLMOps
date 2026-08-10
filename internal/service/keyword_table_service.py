#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关键词表服务

@Author :   Xinkang Wu
@Time   :   2026/8/2 17:29
@File   :   keyword_table_service.py
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from redis import Redis

from internal.entity.cache_entity import LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE, LOCK_EXPIRE_TIME
from internal.model import KeywordTable, Segment
from internal.service import BaseService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class KeywordTableService(BaseService):
    """知识库关键词表服务"""

    db: SQLAlchemy
    redis_client: Redis

    def add_keyword_table_from_segment_ids(self, dataset_id: UUID, segment_ids: list[UUID]) -> None:
        """添加片段列表到知识库关键词表"""

        # 获取分布式锁
        cache_key = LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE.format(dataset_id=dataset_id)
        with self.redis_client.lock(cache_key, timeout=LOCK_EXPIRE_TIME):
            # 获取知识库的关键词表
            keyword_table_record = self.get_keyword_table_from_dataset_id(dataset_id)
            keyword_table = {
                field: set(value) for field, value in keyword_table_record.keyword_table.items()
            }

            # 获取片段列表对应的关键词列表
            segments = self.db.session.query(Segment).with_entities(Segment.id, Segment.keywords).filter(
                Segment.id.in_(segment_ids)
            ).all()

            # 将新关键词添加到关键词表中
            for id, keywords in segments:
                for keyword in keywords:
                    if keyword not in keyword_table:
                        keyword_table[keyword] = set()
                    keyword_table[keyword].add(str(id))

            # 更新关键词表
            self.update(
                keyword_table_record,
                keyword_table={field: list(value) for field, value in keyword_table.items()}
            )

    def get_keyword_table_from_dataset_id(self, dataset_id: UUID) -> KeywordTable:
        """获取知识库的关键词表"""

        keyword_table = self.db.session.query(KeywordTable).filter(
            KeywordTable.dataset_id == dataset_id,
        ).one_or_none()

        if keyword_table is None:
            keyword_table = self.create(KeywordTable, dataset_id=dataset_id, keyword_table={})

        return keyword_table

    def delete_keyword_table_from_segment_ids(self, dataset_id: UUID, segment_ids: list[UUID]) -> None:
        """删除知识库关键词表中的片段列表"""

        # 获取分布式锁
        cache_key = LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE.format(dataset_id=dataset_id)
        with self.redis_client.lock(cache_key, timeout=LOCK_EXPIRE_TIME):
            # 获取当前知识库的关键词表
            keyword_table_record = self.get_keyword_table_from_dataset_id(dataset_id)
            keyword_table = keyword_table_record.keyword_table.copy()  # 包含引用类型，必须深拷贝后更新，否则框架无法判断是否有更新

            # 待删除的片段ID和关键词
            segment_ids_to_delete = set([str(segment_id) for segment_id in segment_ids])
            keywords_to_delete = set()

            # 删除关键词表中的待删除片段
            for keyword, segment_ids in keyword_table.items():
                segment_ids_set = set(segment_ids)
                # 判断该关键词是否存在待删除片段
                if segment_ids_to_delete.intersection(segment_ids_set):
                    # 删除关键词表中的相应片段
                    keyword_table[keyword] = list(segment_ids_set.difference(segment_ids_to_delete))
                    # 若该关键词对应片段为空，将该关键词加入待删除集合
                    if not keyword_table[keyword]:
                        keywords_to_delete.add(keyword)

            # 删除空关键词
            for keyword in keywords_to_delete:
                del keyword_table[keyword]

            # 更新至关键词表DB
            self.update(keyword_table_record, keyword_table=keyword_table)
