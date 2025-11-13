#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
凡人小说文本切块WorkUnit
负责加载小说文件，进行章节切块，并存储到SQLite数据库中
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Optional

from src.rmod.fanran_chapter_chunk_module import ChapterChunkExtractor
from src.store.sqlite_conn import get_sqlite_db
from src.store.sqlite_repo import ChapterChunkRepo
from src.models import ChapterChunk

# Configure logger
logger = logging.getLogger(__name__)

class FanrenTextChunkWorkUnit:
    """凡人小说文本切块工作单元"""

    def __init__(self, novel_file_path: str, novel_name: str = "fanren"):
        """
        初始化工作单元

        Args:
            novel_file_path: 小说文件路径
            novel_name: 小说名称，默认为"fanren"
        """
        self.novel_file_path = novel_file_path
        self.novel_name = novel_name
        self.chunks: Optional[List[ChapterChunk]] = None

    def load_novel_text(self) -> str:
        """
        加载小说文件内容

        Returns:
            str: 小说文本内容

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码问题
        """
        file_path = Path(self.novel_file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"小说文件不存在: {self.novel_file_path}")

        # 尝试不同的编码
        encodings = ['gb18030', 'gbk', 'utf-8', 'utf-8-sig']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.info(f"✓ 使用编码 {encoding} 成功读取文件")
                logger.info(f"✓ 文件大小: {len(content):,} 字符")
                return content
            except UnicodeDecodeError as e:
                logger.warning(f"✗ 编码 {encoding} 失败: {e}")
                continue
            except Exception as e:
                logger.warning(f"✗ 读取文件时发生错误: {e}")
                continue

        raise Exception("所有编码都失败，无法读取文件")

    def extract_chunks(self, raw_text: str) -> List[ChapterChunk]:
        """
        提取章节块

        Args:
            raw_text: 小说原始文本

        Returns:
            List[ChapterChunk]: 章节块列表
        """
        logger.info("开始提取章节块...")
        chunks = ChapterChunkExtractor.extract_chapter_chunks(self.novel_name, raw_text)

        logger.info(f"✓ 总共提取了 {len(chunks)} 个章节块")

        # 统计信息
        empty_chunks = [chunk for chunk in chunks if chunk.token_count == 0]
        valid_chunks = [chunk for chunk in chunks if chunk.token_count > 0]

        logger.info(f"  - 有效章节: {len(valid_chunks)} 个")
        logger.info(f"  - 空章节: {len(empty_chunks)} 个")

        if valid_chunks:
            total_tokens = sum(chunk.token_count for chunk in valid_chunks)
            avg_tokens = total_tokens / len(valid_chunks)
            logger.info(f"  - 平均token数: {avg_tokens:.1f}")
            logger.info(f"  - 总token数: {total_tokens:,}")

        self.chunks = chunks
        return chunks

    def save_to_database(self, chunks: List[ChapterChunk]) -> int:
        """
        保存章节块到数据库

        Args:
            chunks: 章节块列表

        Returns:
            int: 成功保存的章节数量
        """
        logger.info("开始保存章节块到数据库...")

        try:
            with get_sqlite_db() as db:
                conn = db.get_connection()
                saved_count = ChapterChunkRepo.upsert_chunks(conn, chunks)
                conn.commit()

                logger.info(f"✓ 成功保存了 {saved_count} 个章节块到数据库")
                return saved_count

        except Exception as e:
            logger.error(f"✗ 保存到数据库失败: {e}")
            raise

    def run(self) -> int:
        """
        执行完整的工作流程

        Returns:
            int: 成功处理的章节数量

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码问题
            Exception: 其他处理错误
        """
        logger.info("=" * 60)
        logger.info("凡人小说文本切块 WorkUnit 开始运行")
        logger.info("=" * 60)

        # 1. 加载小说文件
        logger.info(f"正在加载小说文件: {self.novel_file_path}")
        raw_text = self.load_novel_text()

        # 2. 提取章节块
        chunks = self.extract_chunks(raw_text)

        # 3. 保存到数据库
        saved_count = self.save_to_database(chunks)

        logger.info("=" * 60)
        logger.info(f"WorkUnit 运行完成! 成功处理 {saved_count} 个章节")
        logger.info("=" * 60)

        return saved_count

    def get_chunks(self) -> List[ChapterChunk]:
        """
        获取最近一次提取的章节块

        Returns:
            List[ChapterChunk]: 章节块列表，如果未提取则返回None
        """
        return self.chunks # type: ignore


def main():
    """主函数，用于测试"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 默认配置
    novel_file = "resources/ignored/1.txt"
    novel_name = "fanren"

    # 检查文件是否存在
    if not Path(novel_file).exists():
        logger.error(f"错误: 文件不存在 {novel_file}")
        logger.error("请确保文件路径正确")
        return 1

    try:
        # 创建并运行工作单元
        workunit = FanrenTextChunkWorkUnit(novel_file, novel_name)
        processed_count = workunit.run()

        logger.info(f"\n处理完成! 共处理了 {processed_count} 个章节")
        return 0

    except Exception as e:
        logger.error(f"\n处理失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())