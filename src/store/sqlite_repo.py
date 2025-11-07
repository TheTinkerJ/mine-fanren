#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite DQL (Data Query Language) 操作
包含章节块的增删改查操作
"""

import sys
import os
from typing import List, Optional, Dict
from sqlite3 import Connection

# 添加 src 目录到 Python 路径，以便导入 models
# sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ''))

from ..models import ChapterChunk


class ChapterChunkRepo:
    """章节块数据仓库类，专注于 chapter_chunks 表的操作"""

    @staticmethod
    def insert_chunk(conn: Connection, chunk: ChapterChunk) -> bool:
        """
        插入或替换单个章节块（幂等操作）
        如果章节块已存在，将替换为新的内容；如果不存在，将插入新记录

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            chunk: 章节块对象

        Returns:
            bool: 操作是否成功（插入或替换都算成功）

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        sql = """
        INSERT OR REPLACE INTO chapter_chunks
        (chunk_id, novel_name, chapter_id, chapter_title, line_start, line_end,
         pos_start, pos_end, char_count, token_count, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            chunk.chunk_id,
            chunk.novel_name,
            chunk.chapter_id,
            chunk.chapter_title,
            chunk.line_start,
            chunk.line_end,
            chunk.pos_start,
            chunk.pos_end,
            chunk.char_count,
            chunk.token_count,
            chunk.content
        )

        cursor = conn.execute(sql, params)
        return cursor.rowcount > 0

    @staticmethod
    def update_chunk(conn: Connection, chunk: ChapterChunk) -> bool:
        """
        更新章节块

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            chunk: 章节块对象

        Returns:
            bool: 更新是否成功

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        sql = """
        UPDATE chapter_chunks
        SET novel_name = ?, chapter_id = ?, chapter_title = ?, line_start = ?, line_end = ?,
            pos_start = ?, pos_end = ?, char_count = ?, token_count = ?, content = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE chunk_id = ?
        """

        params = (
            chunk.novel_name,
            chunk.chapter_id,
            chunk.chapter_title,
            chunk.line_start,
            chunk.line_end,
            chunk.pos_start,
            chunk.pos_end,
            chunk.char_count,
            chunk.token_count,
            chunk.content,
            chunk.chunk_id
        )

        cursor = conn.execute(sql, params)
        return cursor.rowcount > 0

    @staticmethod
    def get_chunks_by_ids(conn: Connection, chunk_ids: List[str]) -> Dict[str, ChapterChunk]:
        """
        批量根据chunk_id查询章节块

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            chunk_ids: 章节块ID列表

        Returns:
            Dict[str, ChapterChunk]: 章节块字典，key为chunk_id，value为章节块对象

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        if not chunk_ids:
            return {}

        # 构建IN查询，使用参数化查询防止SQL注入
        placeholders = ','.join(['?' for _ in chunk_ids])
        sql = f"SELECT * FROM chapter_chunks WHERE chunk_id IN ({placeholders})"

        cursor = conn.execute(sql, chunk_ids)
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            chunk = ChapterChunkRepo._row_to_chunk(row)
            result[chunk.chunk_id] = chunk

        return result


    @staticmethod
    def get_chunks_by_chapter_ids(conn: Connection, novel_name: str, chapter_ids: List[int]) -> Dict[int, ChapterChunk]:
        """
        批量根据小说名称和章节ID查询章节块

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            novel_name: 小说名称
            chapter_ids: 章节ID列表

        Returns:
            Dict[int, ChapterChunk]: 章节块字典，key为chapter_id，value为章节块对象

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        if not chapter_ids:
            return {}

        # 构建IN查询，使用参数化查询防止SQL注入
        placeholders = ','.join(['?' for _ in chapter_ids])
        sql = f"SELECT * FROM chapter_chunks WHERE novel_name = ? AND chapter_id IN ({placeholders})"

        # 参数列表：第一个是novel_name，后面是chapter_ids
        params = [novel_name] + chapter_ids
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            chunk = ChapterChunkRepo._row_to_chunk(row)
            result[chunk.chapter_id] = chunk

        return result

    @staticmethod
    def delete_chunk(conn: Connection, chunk_id: str) -> bool:
        """
        删除章节块

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            chunk_id: 章节块ID

        Returns:
            bool: 删除是否成功

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        sql = "DELETE FROM chapter_chunks WHERE chunk_id = ?"

        cursor = conn.execute(sql, (chunk_id,))
        return cursor.rowcount > 0

    
    @staticmethod
    def _row_to_chunk(row) -> ChapterChunk:
        """
        将数据库行转换为ChapterChunk对象

        Args:
            row: 数据库行对象

        Returns:
            ChapterChunk: 章节块对象
        """
        return ChapterChunk.create_chunk(
            novel_name=row['novel_name'],
            chapter_id=row['chapter_id'],
            chapter_title=row['chapter_title'],
            content=row['content'] or '',
            line_start=row['line_start'] or 0,
            line_end=row['line_end'] or 0,
            pos_start=row['pos_start'] or 0,
            pos_end=row['pos_end'] or 0,
            token_count=row['token_count'] or 0
        )