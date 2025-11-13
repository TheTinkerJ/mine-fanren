#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite DQL (Data Query Language) 操作
包含章节块的增删改查操作
"""
from typing import List, Dict
from sqlite3 import Connection
from src.models import ChapterChunk, ChapterChunkTask, EntityExtraction, RelationExtraction, ClaimExtraction


class ChapterChunkRepo:
    """章节块数据仓库类，专注于 chapter_chunks 表的操作"""

    @staticmethod
    def upsert_chunks(conn: Connection, chunks: List[ChapterChunk]) -> int:
        """
        批量插入或更新章节块（批量UPSERT操作）
        批量处理多个章节块，大幅提升性能

        Args:
            conn: 数据库连接对象（由上层管理生命周期）
            chunks: 章节块对象列表

        Returns:
            int: 成功处理的章节数量
        """
        if not chunks:
            return 0

        sql = """
        INSERT INTO chapter_chunks
        (chunk_id, novel_name, chapter_id, chapter_title, line_start, line_end,
         pos_start, pos_end, char_count, token_count, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(chunk_id) DO UPDATE SET
            novel_name = excluded.novel_name,
            chapter_id = excluded.chapter_id,
            chapter_title = excluded.chapter_title,
            line_start = excluded.line_start,
            line_end = excluded.line_end,
            pos_start = excluded.pos_start,
            pos_end = excluded.pos_end,
            char_count = excluded.char_count,
            token_count = excluded.token_count,
            content = excluded.content,
            updated_at = CURRENT_TIMESTAMP
        """

        # 构建批量参数
        params_list = []
        for chunk in chunks:
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
            params_list.append(params)

        # 执行批量操作
        cursor = conn.executemany(sql, params_list)
        return cursor.rowcount

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


class ChapterChunkTaskRepo:
    """章节块任务数据仓库类，专注于 chapter_chunk_task 表的操作"""

    @staticmethod
    def upsert_task(conn: Connection, task: ChapterChunkTask) -> int:
        """
        插入或更新任务（UPSERT操作）

        Args:
            conn: 数据库连接对象
            task: 任务对象

        Returns:
            int: 成功处理的行数
        """
        sql = """
        INSERT INTO chapter_chunk_task
        (task_id, chunk_id, task_type, task_status, created_at, started_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(chunk_id, task_type) DO UPDATE SET
            task_id = excluded.task_id,
            task_status = excluded.task_status,
            started_at = excluded.started_at,
            completed_at = excluded.completed_at
        """

        params = (
            task.task_id,
            task.chunk_id,
            task.task_type,
            task.task_status,
            task.created_at,
            task.started_at,
            task.completed_at
        )

        cursor = conn.execute(sql, params)
        return cursor.rowcount

    @staticmethod
    def get_task(conn: Connection, chunk_id: str, task_type: str) -> ChapterChunkTask | None:
        """
        根据chunk_id和task_type获取任务

        Args:
            conn: 数据库连接对象
            chunk_id: 章节块ID
            task_type: 任务类型

        Returns:
            ChapterChunkTask | None: 任务对象，如果不存在则返回None
        """
        sql = "SELECT * FROM chapter_chunk_task WHERE chunk_id = ? AND task_type = ?"
        cursor = conn.execute(sql, (chunk_id, task_type))
        row = cursor.fetchone()

        if row:
            return ChapterChunkTaskRepo._row_to_task(row)
        return None

    @staticmethod
    def get_pending_tasks(conn: Connection, task_type: str, limit: int = 100) -> List[ChapterChunkTask]:
        """
        获取指定类型的待处理任务

        Args:
            conn: 数据库连接对象
            task_type: 任务类型
            limit: 限制返回数量，默认100

        Returns:
            List[ChapterChunkTask]: 待处理任务列表
        """
        sql = """
        SELECT * FROM chapter_chunk_task
        WHERE task_type = ? AND task_status = 'pending'
        ORDER BY created_at ASC
        LIMIT ?
        """
        cursor = conn.execute(sql, (task_type, limit))
        rows = cursor.fetchall()

        return [ChapterChunkTaskRepo._row_to_task(row) for row in rows]

    @staticmethod
    def _row_to_task(row) -> ChapterChunkTask:
        """
        将数据库行转换为ChapterChunkTask对象

        Args:
            row: 数据库行对象

        Returns:
            ChapterChunkTask: 任务对象
        """
        return ChapterChunkTask(
            task_id=row['task_id'],
            chunk_id=row['chunk_id'],
            task_type=row['task_type'],
            task_status=row['task_status'],
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at']
        )


class EntityExtractionRepo:
    """实体抽取记录数据仓库类，专注于 entity_extractions 表的操作"""

    @staticmethod
    def insert_extractions(conn: Connection, extractions: List[EntityExtraction]) -> int:
        """
        批量插入实体抽取记录

        Args:
            conn: 数据库连接对象
            extractions: 实体抽取记录列表

        Returns:
            int: 成功插入的记录数量
        """
        if not extractions:
            return 0

        sql = """
        INSERT INTO entity_extractions
        (chunk_id, task_id, entity_name, entity_category, entity_description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        params_list = []
        for extraction in extractions:
            params = (
                extraction.chunk_id,
                extraction.task_id,
                extraction.entity_name,
                extraction.entity_category,
                extraction.entity_description,
                extraction.created_at
            )
            params_list.append(params)

        cursor = conn.executemany(sql, params_list)
        return cursor.rowcount

    @staticmethod
    def get_extractions_by_chunk_id(conn: Connection, chunk_id: str) -> List[EntityExtraction]:
        """
        根据章节块ID获取实体抽取记录

        Args:
            conn: 数据库连接对象
            chunk_id: 章节块ID

        Returns:
            List[EntityExtraction]: 实体抽取记录列表
        """
        sql = "SELECT * FROM entity_extractions WHERE chunk_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (chunk_id,))
        rows = cursor.fetchall()

        return [EntityExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def get_extractions_by_task_id(conn: Connection, task_id: str) -> List[EntityExtraction]:
        """
        根据任务ID获取实体抽取记录

        Args:
            conn: 数据库连接对象
            task_id: 任务ID

        Returns:
            List[EntityExtraction]: 实体抽取记录列表
        """
        sql = "SELECT * FROM entity_extractions WHERE task_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (task_id,))
        rows = cursor.fetchall()

        return [EntityExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def search_by_entity_name(conn: Connection, entity_name: str, limit: int = 100) -> List[EntityExtraction]:
        """
        根据实体名称搜索抽取记录

        Args:
            conn: 数据库连接对象
            entity_name: 实体名称
            limit: 限制返回数量

        Returns:
            List[EntityExtraction]: 实体抽取记录列表
        """
        sql = """
        SELECT * FROM entity_extractions
        WHERE entity_name = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        cursor = conn.execute(sql, (entity_name, limit))
        rows = cursor.fetchall()

        return [EntityExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def _row_to_extraction(row) -> EntityExtraction:
        """
        将数据库行转换为EntityExtraction对象

        Args:
            row: 数据库行对象

        Returns:
            EntityExtraction: 实体抽取记录对象
        """
        return EntityExtraction(
            extraction_id=row['extraction_id'],
            chunk_id=row['chunk_id'],
            task_id=row['task_id'],
            entity_name=row['entity_name'],
            entity_category=row['entity_category'],
            entity_description=row['entity_description'],
            created_at=row['created_at']
        )


class RelationExtractionRepo:
    """关系抽取记录数据仓库类，专注于 relation_extractions 表的操作"""

    @staticmethod
    def insert_extractions(conn: Connection, extractions: List[RelationExtraction]) -> int:
        """
        批量插入关系抽取记录

        Args:
            conn: 数据库连接对象
            extractions: 关系抽取记录列表

        Returns:
            int: 成功插入的记录数量
        """
        if not extractions:
            return 0

        sql = """
        INSERT INTO relation_extractions
        (chunk_id, task_id, source_entity, target_entity, relationship_type, relationship_description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params_list = []
        for extraction in extractions:
            params = (
                extraction.chunk_id,
                extraction.task_id,
                extraction.source_entity,
                extraction.target_entity,
                extraction.relationship_type,
                extraction.relationship_description,
                extraction.created_at
            )
            params_list.append(params)

        cursor = conn.executemany(sql, params_list)
        return cursor.rowcount

    @staticmethod
    def get_extractions_by_chunk_id(conn: Connection, chunk_id: str) -> List[RelationExtraction]:
        """
        根据章节块ID获取关系抽取记录

        Args:
            conn: 数据库连接对象
            chunk_id: 章节块ID

        Returns:
            List[RelationExtraction]: 关系抽取记录列表
        """
        sql = "SELECT * FROM relation_extractions WHERE chunk_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (chunk_id,))
        rows = cursor.fetchall()

        return [RelationExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def get_extractions_by_task_id(conn: Connection, task_id: str) -> List[RelationExtraction]:
        """
        根据任务ID获取关系抽取记录

        Args:
            conn: 数据库连接对象
            task_id: 任务ID

        Returns:
            List[RelationExtraction]: 关系抽取记录列表
        """
        sql = "SELECT * FROM relation_extractions WHERE task_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (task_id,))
        rows = cursor.fetchall()

        return [RelationExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def search_by_entity(conn: Connection, entity_name: str, limit: int = 100) -> List[RelationExtraction]:
        """
        根据实体名称搜索相关关系记录

        Args:
            conn: 数据库连接对象
            entity_name: 实体名称
            limit: 限制返回数量

        Returns:
            List[RelationExtraction]: 关系抽取记录列表
        """
        sql = """
        SELECT * FROM relation_extractions
        WHERE source_entity = ? OR target_entity = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        cursor = conn.execute(sql, (entity_name, entity_name, limit))
        rows = cursor.fetchall()

        return [RelationExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def _row_to_extraction(row) -> RelationExtraction:
        """
        将数据库行转换为RelationExtraction对象

        Args:
            row: 数据库行对象

        Returns:
            RelationExtraction: 关系抽取记录对象
        """
        return RelationExtraction(
            extraction_id=row['extraction_id'],
            chunk_id=row['chunk_id'],
            task_id=row['task_id'],
            source_entity=row['source_entity'],
            target_entity=row['target_entity'],
            relationship_type=row['relationship_type'],
            relationship_description=row['relationship_description'],
            created_at=row['created_at']
        )


class ClaimExtractionRepo:
    """事实陈述抽取记录数据仓库类，专注于 claim_extractions 表的操作"""

    @staticmethod
    def insert_extractions(conn: Connection, extractions: List[ClaimExtraction]) -> int:
        """
        批量插入事实陈述抽取记录

        Args:
            conn: 数据库连接对象
            extractions: 事实陈述抽取记录列表

        Returns:
            int: 成功插入的记录数量
        """
        if not extractions:
            return 0

        sql = """
        INSERT INTO claim_extractions
        (chunk_id, task_id, claim_category, claim_subject, claim_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        params_list = []
        for extraction in extractions:
            params = (
                extraction.chunk_id,
                extraction.task_id,
                extraction.claim_category,
                extraction.claim_subject,
                extraction.claim_content,
                extraction.created_at
            )
            params_list.append(params)

        cursor = conn.executemany(sql, params_list)
        return cursor.rowcount

    @staticmethod
    def get_extractions_by_chunk_id(conn: Connection, chunk_id: str) -> List[ClaimExtraction]:
        """
        根据章节块ID获取事实陈述抽取记录

        Args:
            conn: 数据库连接对象
            chunk_id: 章节块ID

        Returns:
            List[ClaimExtraction]: 事实陈述抽取记录列表
        """
        sql = "SELECT * FROM claim_extractions WHERE chunk_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (chunk_id,))
        rows = cursor.fetchall()

        return [ClaimExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def get_extractions_by_task_id(conn: Connection, task_id: str) -> List[ClaimExtraction]:
        """
        根据任务ID获取事实陈述抽取记录

        Args:
            conn: 数据库连接对象
            task_id: 任务ID

        Returns:
            List[ClaimExtraction]: 事实陈述抽取记录列表
        """
        sql = "SELECT * FROM claim_extractions WHERE task_id = ? ORDER BY created_at"
        cursor = conn.execute(sql, (task_id,))
        rows = cursor.fetchall()

        return [ClaimExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def search_by_category(conn: Connection, claim_category: str, limit: int = 100) -> List[ClaimExtraction]:
        """
        根据事实类别搜索抽取记录

        Args:
            conn: 数据库连接对象
            claim_category: 事实类别
            limit: 限制返回数量

        Returns:
            List[ClaimExtraction]: 事实陈述抽取记录列表
        """
        sql = """
        SELECT * FROM claim_extractions
        WHERE claim_category = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        cursor = conn.execute(sql, (claim_category, limit))
        rows = cursor.fetchall()

        return [ClaimExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def search_by_subject(conn: Connection, claim_subject: str, limit: int = 100) -> List[ClaimExtraction]:
        """
        根据事实主体搜索抽取记录

        Args:
            conn: 数据库连接对象
            claim_subject: 事实主体
            limit: 限制返回数量

        Returns:
            List[ClaimExtraction]: 事实陈述抽取记录列表
        """
        sql = """
        SELECT * FROM claim_extractions
        WHERE claim_subject = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        cursor = conn.execute(sql, (claim_subject, limit))
        rows = cursor.fetchall()

        return [ClaimExtractionRepo._row_to_extraction(row) for row in rows]

    @staticmethod
    def _row_to_extraction(row) -> ClaimExtraction:
        """
        将数据库行转换为ClaimExtraction对象

        Args:
            row: 数据库行对象

        Returns:
            ClaimExtraction: 事实陈述抽取记录对象
        """
        return ClaimExtraction(
            extraction_id=row['extraction_id'],
            chunk_id=row['chunk_id'],
            task_id=row['task_id'],
            claim_category=row['claim_category'],
            claim_subject=row['claim_subject'],
            claim_content=row['claim_content'],
            created_at=row['created_at']
        )