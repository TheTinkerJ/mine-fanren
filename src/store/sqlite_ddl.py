#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite DDL (Data Definition Language) 定义
包含表结构、索引等的创建语句
"""

import sqlite3
from typing import List
from sqlite3 import Connection
from src.store.sqlite_types import SQLiteStorageError


# 章节块表创建语句
CREATE_CHAPTER_CHUNKS_TABLE = """
CREATE TABLE IF NOT EXISTS chapter_chunks (
    chunk_id TEXT PRIMARY KEY,
    novel_name TEXT NOT NULL,
    chapter_id INTEGER NOT NULL,
    chapter_title TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    pos_start INTEGER,
    pos_end INTEGER,
    char_count INTEGER,
    token_count INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(novel_name, chapter_id)
);
"""

# 章节块任务表创建语句
CREATE_CHAPTER_CHUNK_TASK_TABLE = """
CREATE TABLE IF NOT EXISTS chapter_chunk_task (
    task_id TEXT PRIMARY KEY,
    chunk_id TEXT NOT NULL,

    -- 任务类型和状态
    task_type TEXT NOT NULL,  -- 'embedding', 'er_claim'
    task_status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- 唯一约束：同一个chunk的同一类型任务只能有一个
    UNIQUE(chunk_id, task_type)
);
"""

# 索引创建语句
INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_novel_name ON chapter_chunks(novel_name);",
    "CREATE INDEX IF NOT EXISTS idx_chapter_id ON chapter_chunks(chapter_id);",
    # chapter_chunk_task 表索引
    "CREATE INDEX IF NOT EXISTS idx_task_status ON chapter_chunk_task(task_status);",
    "CREATE INDEX IF NOT EXISTS idx_task_type ON chapter_chunk_task(task_type);",
    "CREATE INDEX IF NOT EXISTS idx_chunk_task ON chapter_chunk_task(chunk_id, task_type);",
]


def create_chapter_chunks_table(conn: Connection) -> None:
    """
    创建章节块表

    Args:
        conn: 数据库连接对象

    Raises:
        SQLiteStorageError: 表创建失败
    """
    try:
        conn.execute(CREATE_CHAPTER_CHUNKS_TABLE)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise SQLiteStorageError(f"创建章节块表失败: {e}")


def create_chapter_chunk_task_table(conn: Connection) -> None:
    """
    创建章节块任务表

    Args:
        conn: 数据库连接对象

    Raises:
        SQLiteStorageError: 表创建失败
    """
    try:
        conn.execute(CREATE_CHAPTER_CHUNK_TASK_TABLE)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise SQLiteStorageError(f"创建章节块任务表失败: {e}")


def create_indexes(conn: Connection) -> None:
    """
    创建索引

    Args:
        conn: 数据库连接对象

    Raises:
        SQLiteStorageError: 索引创建失败
    """
    try:
        for index_sql in INDEX_STATEMENTS:
            conn.execute(index_sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise SQLiteStorageError(f"创建索引失败: {e}")


def init_database(conn: Connection) -> None:
    """
    初始化数据库（创建表和索引）

    Args:
        conn: 数据库连接对象

    Raises:
        SQLiteStorageError: 数据库初始化失败
    """
    try:
        # 创建表
        create_chapter_chunks_table(conn)
        create_chapter_chunk_task_table(conn)
        # 创建索引
        create_indexes(conn)
    except Exception as e:
        raise SQLiteStorageError(f"数据库初始化失败: {e}")


def drop_chapter_chunks_table(conn: Connection) -> None:
    """
    删除章节块表（用于测试或重建）

    Args:
        conn: 数据库连接对象

    Raises:
        SQLiteStorageError: 表删除失败
    """
    try:
        conn.execute("DROP TABLE IF EXISTS chapter_chunks;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise SQLiteStorageError(f"删除章节块表失败: {e}")


def get_table_info(conn: Connection, table_name: str) -> List[sqlite3.Row]:
    """
    获取表结构信息

    Args:
        conn: 数据库连接对象
        table_name: 表名

    Returns:
        List[sqlite3.Row]: 表结构信息列表
    """
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()