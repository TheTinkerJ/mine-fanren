#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite DQL (Data Query Language) 操作
包含章节块的增删改查操作
"""

import sys
import os
from typing import List, Optional

# 添加 src 目录到 Python 路径，以便导入 models
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ''))

from models import ChapterChunk
from .sqlite_conn import get_sqlite_db
from .sqlite_types import SQLiteStorageError, DuplicateChunkError, ChunkNotFoundError


class ChapterChunkRepo:
    """章节块数据仓库类，专注于 chapter_chunks 表的操作"""

    @staticmethod
    def insert_chunk(chunk: ChapterChunk) -> bool:
        """
        插入单个章节块

        Args:
            chunk: 章节块对象

        Returns:
            bool: 插入是否成功

        Raises:
            DuplicateChunkError: 章节块已存在
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()

            sql = """
            INSERT INTO chapter_chunks
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

            try:
                cursor = conn.execute(sql, params)
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                conn.rollback()
                if "UNIQUE constraint failed" in str(e):
                    raise DuplicateChunkError(f"章节块已存在: {chunk.chunk_id}")
                raise SQLiteStorageError(f"插入章节块失败: {e}")

    @staticmethod
    def get_chunk_by_id(chunk_id: str) -> Optional[ChapterChunk]:
        """
        根据chunk_id查询章节块

        Args:
            chunk_id: 章节块ID

        Returns:
            Optional[ChapterChunk]: 章节块对象，如果不存在则返回None

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()
            sql = "SELECT * FROM chapter_chunks WHERE chunk_id = ?"

            try:
                cursor = conn.execute(sql, (chunk_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                return ChapterChunkRepo._row_to_chunk(row)
            except Exception as e:
                raise SQLiteStorageError(f"查询章节块失败: {e}")

    @staticmethod
    def get_chunks_by_novel(novel_name: str) -> List[ChapterChunk]:
        """
        查询指定小说的所有章节块

        Args:
            novel_name: 小说名称

        Returns:
            List[ChapterChunk]: 章节块列表

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()
            sql = "SELECT * FROM chapter_chunks WHERE novel_name = ? ORDER BY chapter_id"

            try:
                cursor = conn.execute(sql, (novel_name,))
                rows = cursor.fetchall()

                return [ChapterChunkRepo._row_to_chunk(row) for row in rows]
            except Exception as e:
                raise SQLiteStorageError(f"查询小说章节失败: {e}")

    @staticmethod
    def get_chunk_by_chapter_id(novel_name: str, chapter_id: int) -> Optional[ChapterChunk]:
        """
        根据小说名称和章节ID查询章节块

        Args:
            novel_name: 小说名称
            chapter_id: 章节ID

        Returns:
            Optional[ChapterChunk]: 章节块对象，如果不存在则返回None

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()
            sql = "SELECT * FROM chapter_chunks WHERE novel_name = ? AND chapter_id = ?"

            try:
                cursor = conn.execute(sql, (novel_name, chapter_id))
                row = cursor.fetchone()

                if row is None:
                    return None

                return ChapterChunkRepo._row_to_chunk(row)
            except Exception as e:
                raise SQLiteStorageError(f"查询章节失败: {e}")

    @staticmethod
    def update_chunk(chunk: ChapterChunk) -> bool:
        """
        更新章节块

        Args:
            chunk: 章节块对象

        Returns:
            bool: 更新是否成功

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()

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

            try:
                cursor = conn.execute(sql, params)
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                conn.rollback()
                raise SQLiteStorageError(f"更新章节块失败: {e}")

    @staticmethod
    def delete_chunk(chunk_id: str) -> bool:
        """
        删除章节块

        Args:
            chunk_id: 章节块ID

        Returns:
            bool: 删除是否成功

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()
            sql = "DELETE FROM chapter_chunks WHERE chunk_id = ?"

            try:
                cursor = conn.execute(sql, (chunk_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                conn.rollback()
                raise SQLiteStorageError(f"删除章节块失败: {e}")

    @staticmethod
    def get_statistics(novel_name: str) -> dict:
        """
        获取小说的统计信息

        Args:
            novel_name: 小说名称

        Returns:
            dict: 统计信息，包含章节数、总字符数、总token数等

        Raises:
            SQLiteStorageError: 数据库操作失败
        """
        with get_sqlite_db() as db:
            conn = db.get_connection()

            sql = """
            SELECT
                COUNT(*) as chapter_count,
                SUM(char_count) as total_chars,
                SUM(token_count) as total_tokens,
                MIN(chapter_id) as min_chapter_id,
                MAX(chapter_id) as max_chapter_id
            FROM chapter_chunks
            WHERE novel_name = ?
            """

            try:
                cursor = conn.execute(sql, (novel_name,))
                row = cursor.fetchone()

                return {
                    'chapter_count': row['chapter_count'] or 0,
                    'total_chars': row['total_chars'] or 0,
                    'total_tokens': row['total_tokens'] or 0,
                    'min_chapter_id': row['min_chapter_id'],
                    'max_chapter_id': row['max_chapter_id']
                }
            except Exception as e:
                raise SQLiteStorageError(f"获取统计信息失败: {e}")

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