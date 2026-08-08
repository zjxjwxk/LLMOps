#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库服务

@Author :   Xinkang Wu
@Time   :   2026/7/26 15:57
@File   :   dataset_service.py
"""
from dataclasses import dataclass
from uuid import UUID

from injector import inject
from sqlalchemy import desc

from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidationException, NotFoundException
from internal.model import Dataset
from internal.schema.dataset_schema import CreateDatasetReq, UpdateDatasetReq, GetDatasetsWithPageReq
from pkg.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class DatasetService(BaseService):
    """知识库服务"""

    db: SQLAlchemy

    def create_dataset(self, req: CreateDatasetReq) -> Dataset:
        """创建知识库"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 检查当前账户是否已存在同名知识库
        dataset = self.db.session.query(Dataset).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()

        if dataset:
            raise ValidationException(f"该知识库名称{req.name.data}已存在")

        # 设置默认描述
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        # 创建知识库记录
        return self.create(
            Dataset,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

    def get_dataset(self, dataset_id: UUID):
        """获取知识库"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 检查当前账户是否存在该知识库
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        return dataset

    def get_datasets_with_page(self, req: GetDatasetsWithPageReq) -> tuple[list[Dataset], Paginator]:
        """获取知识库分页"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 构建筛选器
        filters = [Dataset.account_id == account_id]
        if req.search_word.data:
            filters.append(Dataset.name.ilike(f"%{req.search_word.data}%"))

        # 分页查询数据
        datasets = paginator.paginate(
            self.db.session.query(Dataset).filter(*filters).order_by(desc("created_at")),
        )

        return datasets, paginator

    def update_dataset(self, dataset_id: UUID, req: UpdateDatasetReq) -> Dataset:
        """更新知识库"""

        # TODO: 实现授权认证模块后，完善账户相关逻辑
        account_id = "05a9c691-a5b0-4661-893a-430c760eb8cd"

        # 检查当前账户是否存在该知识库
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 检查更新后的知识库名称是否已存在（不包括当前请求的dataset_id）
        check_dataset = self.db.session.query(Dataset).filter(
            Dataset.account_id == account_id,
            Dataset.name == req.name.data,
            Dataset.id != dataset_id,
        ).one_or_none()

        if check_dataset:
            raise ValidationException(f"该知识库名称{req.name.data}已存在")

        # 设置默认描述
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        # 更新知识库
        self.update(
            dataset,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.data,
        )

        return dataset
