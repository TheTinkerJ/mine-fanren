#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 存储模块
提供 ChapterChunk 的 SQLite 数据库存储功能
"""

from src.store.sqlite_conn import SqliteDB, get_sqlite_db
from src.store.sqlite_repo import ChapterChunkRepo
from src.store.sqlite_types import SQLiteStorageError

__all__ = [
    # 核心接口
    'SqliteDB',
    'ChapterChunkRepo',
    'get_sqlite_db',

    # 异常类型
    'SQLiteStorageError',
]