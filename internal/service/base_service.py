#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础服务

@Author :   Xinkang Wu
@Time   :   2026/7/4 13:33
@File   :   base_service.py
"""
from typing import Any, Optional

from internal.exception import FailException
from pkg.sqlalchemy import SQLAlchemy


class BaseService:
    """基础服务"""

    db: SQLAlchemy

    def create(self, model: Any, **kwargs) -> Any:
        """插入数据库记录"""

        with self.db.auto_commit():
            model_instance = model(**kwargs)
            self.db.session.add(model_instance)
        return model_instance

    def delete(self, model_instance: Any) -> Any:
        """删除数据库记录"""

        with self.db.auto_commit():
            self.db.session.delete(model_instance)
        return model_instance

    def update(self, model_instance: Any, **kwargs) -> Any:
        """更新数据库记录"""

        with self.db.auto_commit():
            for field, value in kwargs.items():
                if hasattr(model_instance, field):
                    setattr(model_instance, field, value)
                else:
                    raise FailException("更新数据库记录失败")
        return model_instance

    def get(self, model: Any, primary_key: Any) -> Optional[Any]:
        """查询数据库记录"""

        return self.db.session.query(model).get(primary_key)
