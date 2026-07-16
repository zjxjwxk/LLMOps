#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/7/16 12:57
@File   :   upload_file_schema.py
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed
from marshmallow import Schema, fields, pre_dump

from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION, ALLOWED_IMAGE_EXTENSION
from internal.model import UploadFile


class UploadFileReq(FlaskForm):
    """上传文件请求"""

    file = FileField("file", validators=[
        FileRequired("上传文件不能为空"),
        FileSize(max_size=15 * 1024 * 1024, message="上传文件的大小不能超过15MB"),
        FileAllowed(ALLOWED_DOCUMENT_EXTENSION,
                    message=f"上传文件的格式不允许，仅允许{'/'.join(ALLOWED_DOCUMENT_EXTENSION)}格式")
    ])


class UploadFileResp(Schema):
    """上传文件响应"""

    id = fields.UUID(default="")
    account_id = fields.UUID(default="")
    name = fields.String(default="")
    key = fields.String(default="")
    size = fields.Integer(default=0)
    extension = fields.String(default="")
    mime_type = fields.String(default="")
    created_at = fields.Integer(default=0)

    @pre_dump
    def process_data(self, data: UploadFile, **kwargs):
        return {
            "id": data.id,
            "account_id": data.account_id,
            "name": data.name,
            "key": data.key,
            "size": data.size,
            "extension": data.extension,
            "mime_type": data.mime_type,
            "created_at": data.created_at.timestamp(),
        }


class UploadImageReq(FlaskForm):
    """上传图片请求"""

    file = FileField("file", validators=[
        FileRequired("上传图片不能为空"),
        FileSize(max_size=15 * 1024 * 1024, message="上传图片的大小不能超过15MB"),
        FileAllowed(ALLOWED_IMAGE_EXTENSION,
                    message=f"上传图片的格式不允许，仅允许{'/'.join(ALLOWED_IMAGE_EXTENSION)}格式")
    ])
