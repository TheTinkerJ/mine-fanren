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

# 实体抽取记录表创建语句
CREATE_ENTITY_EXTRactions_TABLE = """
CREATE TABLE IF NOT EXISTS entity_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT NOT NULL,
    task_id TEXT NOT NULL,

    -- 抽取结果字段
    entity_name TEXT NOT NULL,
    entity_category TEXT NOT NULL,
    entity_description TEXT,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
);
"""

# 关系抽取记录表创建语句
CREATE_RELATION_EXTRactions_TABLE = """
CREATE TABLE IF NOT EXISTS relation_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT NOT NULL,
    task_id TEXT NOT NULL,

    -- 抽取结果字段
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship_type TEXT,
    relationship_description TEXT,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
);
"""

# 事实陈述抽取记录表创建语句
CREATE_CLAIM_EXTRactions_TABLE = """
CREATE TABLE IF NOT EXISTS claim_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT NOT NULL,
    task_id TEXT NOT NULL,

    -- 抽取结果字段
    claim_category TEXT NOT NULL,
    claim_subject TEXT NOT NULL,
    claim_content TEXT NOT NULL,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
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

    # entity_extractions 表索引
    "CREATE INDEX IF NOT EXISTS idx_entity_chunk ON entity_extractions(chunk_id);",
    "CREATE INDEX IF NOT EXISTS idx_entity_task ON entity_extractions(task_id);",
    "CREATE INDEX IF NOT EXISTS idx_entity_name ON entity_extractions(entity_name);",
    "CREATE INDEX IF NOT EXISTS idx_entity_category ON entity_extractions(entity_category);",
    "CREATE INDEX IF NOT EXISTS idx_entity_created_at ON entity_extractions(created_at);",

    # relation_extractions 表索引
    "CREATE INDEX IF NOT EXISTS idx_relation_chunk ON relation_extractions(chunk_id);",
    "CREATE INDEX IF NOT EXISTS idx_relation_task ON relation_extractions(task_id);",
    "CREATE INDEX IF NOT EXISTS idx_relation_source ON relation_extractions(source_entity);",
    "CREATE INDEX IF NOT EXISTS idx_relation_target ON relation_extractions(target_entity);",
    "CREATE INDEX IF NOT EXISTS idx_relation_type ON relation_extractions(relationship_type);",
    "CREATE INDEX IF NOT EXISTS idx_relation_created_at ON relation_extractions(created_at);",

    # claim_extractions 表索引
    "CREATE INDEX IF NOT EXISTS idx_claim_chunk ON claim_extractions(chunk_id);",
    "CREATE INDEX IF NOT EXISTS idx_claim_task ON claim_extractions(task_id);",
    "CREATE INDEX IF NOT EXISTS idx_claim_category ON claim_extractions(claim_category);",
    "CREATE INDEX IF NOT EXISTS idx_claim_subject ON claim_extractions(claim_subject);",
    "CREATE INDEX IF NOT EXISTS idx_claim_created_at ON claim_extractions(created_at);",
]


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
        conn.execute(CREATE_CHAPTER_CHUNKS_TABLE)
        conn.execute(CREATE_CHAPTER_CHUNK_TASK_TABLE)
        conn.execute(CREATE_ENTITY_EXTRactions_TABLE)
        conn.execute(CREATE_RELATION_EXTRactions_TABLE)
        conn.execute(CREATE_CLAIM_EXTRactions_TABLE)

        # 创建索引
        for index_sql in INDEX_STATEMENTS:
            conn.execute(index_sql)

        conn.commit()
    except Exception as e:
        conn.rollback()
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