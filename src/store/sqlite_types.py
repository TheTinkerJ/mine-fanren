#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 存储模块类型定义
包含异常类和类型提示
"""


class SQLiteStorageError(Exception):
    """SQLite 存储操作异常基类"""
    pass


class DuplicateChunkError(SQLiteStorageError):
    """重复章节块异常"""
    pass


class ChunkNotFoundError(SQLiteStorageError):
    """章节块未找到异常"""
    pass