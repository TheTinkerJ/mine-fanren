#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
定义章节块提取过程中使用的数据结构
"""

from pydantic import BaseModel, Field
import uuid
from typing import Optional


class ChapterChunk(BaseModel):
    """章节块数据结构"""
    novel_name: str = Field(description="小说名称")
    chunk_id: str = Field(description="章节块唯一标识符(UUID)")
    chapter_id: int = Field(description="章节编号")
    chapter_title: str = Field(description="章节标题")

    # 位置信息
    line_start: int = Field(description="开始行号")
    line_end: int = Field(description="结束行号")
    pos_start: int = Field(description="在原文中的字符开始位置")
    pos_end: int = Field(description="在原文中的字符结束位置")

    # 统计信息
    char_count: int = Field(description="字符数")
    token_count: int = Field(description="词元数")

    # 内容
    content: str = Field(description="章节内容")

    @classmethod
    def create_chunk(
        cls,
        novel_name: str,
        chapter_id: int,
        chapter_title: str,
        content: str,
        line_start: int,
        line_end: int,
        pos_start: int,
        pos_end: int,
        token_count: int
    ) -> "ChapterChunk":
        """
        创建章节块实例

        Args:
            novel_name: 小说名称
            chapter_id: 章节编号
            chapter_title: 章节标题
            content: 章节内容
            line_start: 开始行号
            line_end: 结束行号
            pos_start: 字符开始位置
            pos_end: 字符结束位置
            token_count: 词元数，如果为None则用字符数估算

        Returns:
            ChapterChunk: 章节块实例
        """
        # 生成不带横线的UUID
        chunk_id = uuid.uuid4().hex.replace('-', '')

        return cls(
            novel_name=novel_name,
            chunk_id=chunk_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            content=content,
            line_start=line_start,
            line_end=line_end,
            pos_start=pos_start,
            pos_end=pos_end,
            char_count=len(content),
            token_count=token_count
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"ChapterChunk(id={self.chapter_id}, title='{self.chapter_title}', novel={self.novel_name})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"ChapterChunk(chunk_id='{self.chunk_id}', novel_name='{self.novel_name}', "
                f"chapter_id={self.chapter_id}, chapter_title='{self.chapter_title}', "
                f"lines={self.line_start}-{self.line_end}, chars={self.char_count})")