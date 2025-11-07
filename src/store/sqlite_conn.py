#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用数据库连接管理器
"""

import sqlite3
from pathlib import Path
from typing import Optional
from .sqlite_ddl import init_database


class SqliteDB:
    """通用SQLite数据库连接管理器"""

    # 数据库配置
    DEFAULT_DB_PATH = "resources/ignored/sqlite.db"
    DB_TIMEOUT = 30.0

    def __init__(self):
        """初始化SQLite数据库管理器"""
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self):
        """上下文管理器入口"""
        self.conn = self._create_connection()
        init_database(self.conn)  # 初始化所有表结构
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动关闭连接"""
        self.close()

    def _create_connection(self) -> sqlite3.Connection:
        """创建数据库连接"""
        # 确保数据库目录存在
        Path(self.DEFAULT_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.DEFAULT_DB_PATH, timeout=self.DB_TIMEOUT)
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        # 设置行工厂，使查询结果按列名访问
        conn.row_factory = sqlite3.Row

        return conn

    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def get_connection(self) -> sqlite3.Connection:
        """获取当前连接，如果未连接则抛出异常"""
        if self.conn is None:
            raise RuntimeError("数据库连接未初始化，请使用 with 语句")
        return self.conn


# 全局SQLite数据库管理器实例
_sqlite_db = SqliteDB()


def get_sqlite_db() -> SqliteDB:
    """获取全局SQLite数据库管理器实例"""
    return _sqlite_db