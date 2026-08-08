#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
缓存实体

@Author :   Xinkang Wu
@Time   :   2026/8/8 17:49
@File   :   cache_entity.py
"""

# 分布式锁过期时间，默认为600秒
LOCK_EXPIRE_TIME = 600

# 更新文档启用状态锁
LOCK_DOCUMENT_UPDATE_ENABLED = "lock:document:update:enabled_{document_id}"
