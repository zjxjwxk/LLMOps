#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档片段处理器

@Author :   Xinkang Wu
@Time   :   2026/8/11 20:48
@File   :   segment_handler.py
"""
from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject

from internal.schema.segment_schema import GetSegmentsWithPageReq, GetSegmentsWithPageResp
from internal.service import SegmentService
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class SegmentHandler:
    """文档片段处理器"""

    segment_service: SegmentService

    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID):
        """获取文档片段列表分页"""

        # 提取请求并校验
        req = GetSegmentsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 调用服务获取文档片段列表分页
        segments, paginator = self.segment_service.get_segments_with_page(dataset_id, document_id, req)

        resp = GetSegmentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(segments), paginator=paginator))

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """获取文档片段详情"""

        pass

    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """更新文档片段启用状态"""

        pass
