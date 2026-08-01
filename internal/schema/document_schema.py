#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档Schema

@Author :   Xinkang Wu
@Time   :   2026/7/31 16:49
@File   :   document_schema.py
"""
import uuid

from flask_wtf import FlaskForm
from marshmallow import Schema, fields, pre_dump
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, AnyOf, ValidationError

from internal.entity.dataset_entity import ProcessType, DEFAULT_PROCESS_RULE
from internal.model import Document
from internal.schema import ListField
from internal.schema.schema import DictField


class CreateDocumentsReq(FlaskForm):
    """创建文档列表请求"""

    upload_file_ids = ListField("upload_file_ids")
    process_type = StringField("process_type", validators=[
        DataRequired("文档处理类型不能为空"),
        AnyOf(values=[ProcessType.AUTOMATIC, ProcessType.CUSTOM], message="处理类型不支持")
    ])
    rule = DictField("rule")

    def validate_upload_file_ids(self, field: ListField) -> None:
        """校验上传文件ID列表"""

        # 校验上传文件ID列表的类型是否为列表
        if not isinstance(field.data, list):
            raise ValidationError("上传文件ID列表的类型必须为列表")

        # 校验上传文件数量是否非空且不超过10个
        if len(field.data) == 0 or len(field.data) > 10:
            raise ValidationError("上传文件数量不能为0且最多10个")

        # 校验上传文件ID是否为UUID
        for upload_file_id in field.data:
            try:
                uuid.UUID(upload_file_id)
            except Exception as e:
                raise ValidationError("上传文件ID的类型必须为UUID")

        # 删除重复的上传文件ID
        field.data = list(dict.fromkeys(field.data))

    def validate_rule(self, field: DictField) -> None:
        """校验文档处理规则"""

        # 处理模式为自动
        if self.process_type.data == ProcessType.AUTOMATIC:
            # 使用默认处理规则
            field.data = DEFAULT_PROCESS_RULE["rule"]
        else:
            # 处理模式为自定义

            # 校验处理规则是否非空
            if not isinstance(field.data, dict) or len(field.data) == 0:
                raise ValidationError("文档处理类型为自定义时，文档处理规则不能为空")

            unique_pre_process_rule_dict = {}
            # 校验预处理规则是否非空且类型为列表
            if "pre_process_rules" not in field.data or not isinstance(field.data["pre_process_rules"], list):
                raise ValidationError("预处理规则的类型必须为列表")

            for pre_process_rule in field.data["pre_process_rules"]:
                # 校验处理规则id是否非空且在支持列表中
                if "id" not in pre_process_rule or pre_process_rule["id"] not in ["remove_extra_space",
                                                                                  "remove_url_and_email"]:
                    raise ValidationError("预处理规则id为空或不支持")

                # 校验预处理规则enabled是否非空且为布尔类型
                if "enabled" not in pre_process_rule or not isinstance(pre_process_rule["enabled"], bool):
                    raise ValidationError("预处理规则enabled为空或非布尔类型")

                # 添加到唯一字典中，过滤重复规则
                unique_pre_process_rule_dict[pre_process_rule["id"]] = {
                    "id": pre_process_rule["id"],
                    "enabled": pre_process_rule["enabled"],
                }

            # 判断预处理规则是否完整
            if len(unique_pre_process_rule_dict) != 2:
                raise ValidationError("预处理规则不完整，请重试")

            # 将唯一字典转换回列表，更新预处理规则
            field.data["pre_process_rules"] = list(unique_pre_process_rule_dict.values())

            # 校验分段配置非空且类型为字典
            if "segment" not in field.data or not isinstance(field.data["segment"], dict):
                raise ValidationError("分段配置为空或非字典类型")

            # 校验分隔符非空且为字符串列表
            if "separators" not in field.data["segment"] or not isinstance(field.data["segment"]["separators"], list):
                raise ValidationError("分隔符列表为空或非列表类型")

            for separator in field.data["segment"]["separators"]:
                if not isinstance(separator, str):
                    raise ValidationError("分隔符列表包含非字符串类型")

            if len(field.data["segment"]["separators"]) == 0:
                raise ValidationError("分隔符列表为空")

            # 校验分块大小非空且类型为整数
            if "chunk_size" not in field.data["segment"] or not isinstance(field.data["segment"]["chunk_size"], int):
                raise ValidationError("分块大小为空或不为整数类型")

            # 校验分块大小范围在100~1000之间
            if field.data["segment"]["chunk_size"] < 100 or field.data["segment"]["chunk_size"] > 1000:
                raise ValidationError("分块大小范围必须在100~1000之间")

            # 校验分块重叠大小
            if "chunk_overlap" not in field.data["segment"] or not isinstance(field.data["segment"]["chunk_overlap"],
                                                                              int):
                raise ValidationError("分块重叠大小为空或不为整数类型")

            # 校验分块重叠大小范围在0~分块大小*0.5之间
            if (field.data["segment"]["chunk_overlap"] < 0 or
                    field.data["segment"]["chunk_overlap"] > field.data["segment"]["chunk_size"] * 0.5):
                raise ValidationError(f"分块重叠大小范围必须在0~{int(field.data['segment']['chunk_size'] * 0.5)}之间")

            # 更新处理规则（忽略多余字段）
            field.data = {
                "pre_process_rules": field.data["pre_process_rules"],
                "segment": {
                    "separators": field.data["segment"]["separators"],
                    "chunk_size": field.data["segment"]["chunk_size"],
                    "chunk_overlap": field.data["segment"]["chunk_overlap"],
                },
            }


class CreateDocumentsResp(Schema):
    """创建文档列表响应"""

    documents = fields.List(fields.Dict, dump_default=[])
    batch = fields.String(dump_default="")

    @pre_dump
    def process_data(self, data: tuple[list[Document], str], **kwargs):
        return {
            "documents": [{
                "id": document.id,
                "name": document.name,
                "status": document.status,
                "created_at": int(document.created_at.timestamp())
            } for document in data[0]],
            "batch": data[1],
        }
