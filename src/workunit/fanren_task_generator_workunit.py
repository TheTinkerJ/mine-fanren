#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务生成工作单元
根据FanrenTextChunkWorkUnit的结果生成指定类型的任务
"""

import logging
from typing import List, Optional
from src.models import ChapterChunkTask
from src.store.sqlite_repo import ChapterChunkRepo, ChapterChunkTaskRepo
from src.store.sqlite_conn import get_sqlite_db

# Configure logger
logger = logging.getLogger(__name__)


class FanrenTaskGeneratorWorkUnit:
    """任务生成工作单元，为章节块生成指定类型的任务"""
    
    def generate_pending_tasks(
        self,
        task_type: str,
        limit: Optional[int] = None
    ) -> List[ChapterChunkTask]:
        """
        生成待处理的任务（为还没有该类型任务的章节块生成任务）

        Args:
            task_type: 用户自定义的任务类型名称
            limit: 生成任务数量限制

        Returns:
            List[ChapterChunkTask]: 生成的任务列表
        """
        logger.info(f"生成待处理任务: task_type={task_type}")

        # 获取还没有该类型任务的章节块
        with get_sqlite_db() as db:
            conn = db.get_connection()
            chunks_without_task = ChapterChunkRepo.get_chunks_without_task_type(conn, task_type)

        if limit:
            chunks_without_task = chunks_without_task[:limit]

        logger.info(f"找到 {len(chunks_without_task)} 个没有 {task_type} 任务的章节块")
        logger.info(f"开始生成任务: task_type={task_type}, chunk_count={len(chunks_without_task)}")

        # 为每个章节块创建任务
        tasks = []
        for chunk in chunks_without_task:
            task = ChapterChunkTask.create_task(
                chunk_id=chunk.chunk_id,
                task_type=task_type,
                task_status="pending"
            )
            tasks.append(task)

        # 保存任务到数据库
        if tasks:
            saved_count = self._save_tasks(tasks)
            logger.info(f"成功保存了 {saved_count} 个 {task_type} 任务")

        logger.info(f"任务生成完成: total={len(tasks)}")
        return tasks

    
    def _save_tasks(self, tasks: List[ChapterChunkTask]) -> int:
        """保存任务到数据库"""
        with get_sqlite_db() as db:
            conn = db.get_connection()
            result = ChapterChunkTaskRepo.batch_insert_tasks(conn, tasks)
            conn.commit()
            return result



# 示例用法
def example_usage():
    """示例用法"""
    logging.basicConfig(level=logging.INFO)

    # 初始化
    task_generator = FanrenTaskGeneratorWorkUnit()

    # 生成待处理任务
    # 示例：用户自定义的任务类型
    tasks = task_generator.generate_pending_tasks("erc", limit=100) # 实体关系陈述 ERC 
    # 或者：tasks = task_generator.generate_pending_tasks("情感分析", limit=50)
    # 或者：tasks = task_generator.generate_pending_tasks("事实抽取", limit=200)

    
    
if __name__ == "__main__":
    example_usage()