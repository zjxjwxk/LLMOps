#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件上传服务

@Author :   Xinkang Wu
@Time   :   2026/7/16 14:19
@File   :   upload_file_service.py
"""
from dataclasses import dataclass

from injector import inject

from internal.model import UploadFile
from pkg.sqlalchemy import SQLAlchemy
from .base_service import BaseService


@inject
@dataclass
class UploadFileService(BaseService):
    """文件上传服务"""

    db: SQLAlchemy

    def create_upload_file(self, **kwargs) -> UploadFile:
        """创建文件上传记录"""

        return self.create(UploadFile, **kwargs)
