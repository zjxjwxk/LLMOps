#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库Schema

@Author :   Xinkang Wu
@Time   :   2026/7/26 14:53
@File   :   dataset_schema.py
"""
from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, Length, URL, Optional, AnyOf, NumberRange

from internal.entity.dataset_entity import RetrievalStrategy
from internal.model import Dataset
from pkg.paginator import PaginatorReq


class CreateDatasetReq(FlaskForm):
    """创建知识库请求"""

    name = StringField("name", validators=[
        DataRequired("知识库名称不能为空"),
        Length(max=100, message="知识库名称长度不能超过100字符")
    ])
    icon = StringField("icon", validators=[
        DataRequired("知识库图标不能为空"),
        URL(message="知识库图标必须为URL格式地址"),
    ])
    description = StringField("description", default="", validators=[
        Optional(),
        Length(max=2000, message="知识库描述长度不能超过2000字符")
    ])


class GetDatasetResp(Schema):
    """获取知识库响应"""

    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    hit_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "hit_count": data.hit_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


class GetDatasetsWithPageReq(PaginatorReq):
    """获取知识库分页请求"""

    search_word = StringField("search_word", default="", validators=[
        Optional()
    ])


class GetDatasetsWithPageResp(Schema):
    """获取知识库分页响应"""

    id = fields.UUID(dump_default="")
    name = fields.String(dump_default="")
    icon = fields.String(dump_default="")
    description = fields.String(dump_default="")
    document_count = fields.Integer(dump_default=0)
    related_app_count = fields.Integer(dump_default=0)
    character_count = fields.Integer(dump_default=0)
    updated_at = fields.Integer(dump_default=0)
    created_at = fields.Integer(dump_default=0)

    @pre_dump
    def process_data(self, data: Dataset, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "description": data.description,
            "document_count": data.document_count,
            "related_app_count": data.related_app_count,
            "character_count": data.character_count,
            "updated_at": int(data.updated_at.timestamp()),
            "created_at": int(data.created_at.timestamp()),
        }


class UpdateDatasetReq(FlaskForm):
    """更新知识库请求"""

    name = StringField("name", validators=[
        DataRequired("知识库名称不能为空"),
        Length(max=100, message="知识库名称长度不能超过100字符")
    ])
    icon = StringField("icon", validators=[
        DataRequired("知识库图标不能为空"),
        URL(message="知识库图标必须为URL格式地址"),
    ])
    description = StringField("description", default="", validators=[
        Optional(),
        Length(max=2000, message="知识库描述长度不能超过2000字符")
    ])


class HitReq(FlaskForm):
    """召回测试请求"""

    query = StringField("query", validators=[
        DataRequired("查询语句不能为空"),
        Length(max=200, message="查询语句长度不能超过200个字符")
    ])
    retrieval_strategy = StringField("retrieval_strategy", validators=[
        DataRequired("检索策略不能为空"),
        AnyOf([item.value for item in RetrievalStrategy], message="检索策略不支持")
    ])
    k = IntegerField("k", validators=[
        DataRequired("最大召回数量不能为空"),
        NumberRange(min=1, max=10, message="最大召回数量的范围必须在1-10之间")
    ])
    score = FloatField("score", validators=[
        NumberRange(min=0, max=0.99, message="最小匹配度的范围必须在0-0.99之间")
    ])
