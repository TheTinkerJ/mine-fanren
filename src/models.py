#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
定义章节块提取过程中使用的数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from src.imod.types import ErExtractEntity, ErExtractRelation, ClaimExtractItem

class PromptTemplate(BaseModel):
    """提示词模板数据结构"""
    template_key: str = Field(description="提示词模板唯一标识符")
    version: str = Field(description="模板版本号 (例如: '1.0.0')")
    description: str = Field(description="模板描述")

    # 模板内容
    template_content: str = Field(description="Python字符串模板内容")
    required_params: list[str] = Field(description="模板所需参数列表", default_factory=list)

    # 元数据
    language: str = Field(description="模板语言", default="zh")
    notes: str = Field(description="备注信息，使用感受、优化建议等", default="")

    @classmethod
    def create_template(
        cls,
        template_key: str,
        version: str,
        description: str,
        template_content: str,
        required_params: list[str] | None = None,
        language: str = "zh",
        notes: str = ""
    ) -> "PromptTemplate":
        """
        创建提示词模板实例

        Args:
            template_key: 模板唯一标识符
            version: 版本号
            description: 模板描述
            template_content: Python字符串模板内容
            required_params: 必需参数列表
            language: 模板语言
            notes: 备注信息

        Returns:
            PromptTemplate: 提示词模板实例
        """
        return cls(
            template_key=template_key,
            version=version,
            description=description,
            template_content=template_content,
            required_params=required_params or [],
            language=language,
            notes=notes
        )

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 模板参数

        Returns:
            str: 渲染后的内容

        Raises:
            ValueError: 缺少必需参数
            KeyError: 参数不存在于模板中
        """
        # 检查必需参数
        missing_params = set(self.required_params) - set(kwargs.keys())
        if missing_params:
            raise ValueError(f"缺少必需参数: {', '.join(missing_params)}")

        try:
            return self.template_content.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"模板中存在未定义的参数: {e}")
        except ValueError as e:
            raise ValueError(f"模板格式错误: {e}")

    def __str__(self) -> str:
        """字符串表示"""
        return f"PromptTemplate(key={self.template_key}, version={self.version})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"PromptTemplate(template_key='{self.template_key}', version='{self.version}', "
                f"required_params={self.required_params}, notes='{self.notes[:50]}...')" if len(self.notes) > 50 else
                f"PromptTemplate(template_key='{self.template_key}', version='{self.version}', "
                f"required_params={self.required_params}, notes='{self.notes})")

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



class ChapterChunkTask(BaseModel):
    """章节块任务数据结构"""
    task_id: str = Field(description="任务唯一标识符(UUID)")
    chunk_id: str = Field(description="章节块唯一标识符")

    # 任务类型和状态
    task_type: str = Field(description="任务类型")
    task_status: str = Field(description="任务状态", default="pending", pattern=r"^(pending|processing|completed|failed)$")

    # 时间戳
    created_at: str = Field(description="创建时间")
    started_at: str | None = Field(description="开始处理时间", default=None)
    completed_at: str | None = Field(description="完成时间", default=None)

    @classmethod
    def create_task(
        cls,
        chunk_id: str,
        task_type: str,
        task_status: str = "pending"
    ) -> "ChapterChunkTask":
        """
        创建章节块任务实例

        Args:
            chunk_id: 章节块唯一标识符
            task_type: 任务类型 ('embedding', 'er_claim')
            task_status: 任务状态，默认为 'pending'

        Returns:
            ChapterChunkTask: 章节块任务实例
        """
        from datetime import datetime

        # 生成不带横线的UUID
        task_id = uuid.uuid4().hex.replace('-', '')
        created_at = datetime.now().isoformat()

        return cls(
            task_id=task_id,
            chunk_id=chunk_id,
            task_type=task_type,
            task_status=task_status,
            created_at=created_at
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"ChapterChunkTask(id={self.task_id}, type={self.task_type}, status={self.task_status})"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"ChapterChunkTask(task_id='{self.task_id}', chunk_id='{self.chunk_id}', "
                f"task_type='{self.task_type}', task_status='{self.task_status}', "
                f"created_at='{self.created_at}')")


class EntityExtraction(BaseModel):
    """实体抽取记录数据结构"""
    extraction_id: int | None = Field(description="抽取记录ID，创建时为None", default=None)
    chunk_id: str = Field(description="章节块唯一标识符")
    task_id: str = Field(description="抽取任务唯一标识符")

    # 抽取结果字段
    entity_name: str = Field(description="实体名称")
    entity_category: str = Field(description="实体类别")
    entity_description: str | None = Field(description="实体描述", default=None)

    # 时间戳
    created_at: str = Field(description="创建时间")

    @classmethod
    def create_extraction(
        cls,
        chunk_id: str,
        task_id: str,
        entity_name: str,
        entity_category: str,
        entity_description: str | None = None
    ) -> "EntityExtraction":
        """
        创建实体抽取记录实例

        Args:
            chunk_id: 章节块唯一标识符
            task_id: 抽取任务唯一标识符
            entity_name: 实体名称
            entity_category: 实体类别
            entity_description: 实体描述

        Returns:
            EntityExtraction: 实体抽取记录实例
        """
        from datetime import datetime
        created_at = datetime.now().isoformat()

        return cls(
            extraction_id=None,
            chunk_id=chunk_id,
            task_id=task_id,
            entity_name=entity_name,
            entity_category=entity_category,
            entity_description=entity_description,
            created_at=created_at
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"EntityExtraction(id={self.extraction_id}, name='{self.entity_name}', category='{self.entity_category}')"


class RelationExtraction(BaseModel):
    """关系抽取记录数据结构"""
    extraction_id: int | None = Field(description="抽取记录ID，创建时为None", default=None)
    chunk_id: str = Field(description="章节块唯一标识符")
    task_id: str = Field(description="抽取任务唯一标识符")

    # 抽取结果字段
    source_entity: str = Field(description="关系源实体")
    target_entity: str = Field(description="关系目标实体")
    relationship_type: str | None = Field(description="关系类型", default=None)
    relationship_description: str | None = Field(description="关系描述", default=None)

    # 时间戳
    created_at: str = Field(description="创建时间")

    @classmethod
    def create_extraction(
        cls,
        chunk_id: str,
        task_id: str,
        source_entity: str,
        target_entity: str,
        relationship_type: str | None = None,
        relationship_description: str | None = None
    ) -> "RelationExtraction":
        """
        创建关系抽取记录实例

        Args:
            chunk_id: 章节块唯一标识符
            task_id: 抽取任务唯一标识符
            source_entity: 关系源实体
            target_entity: 关系目标实体
            relationship_type: 关系类型
            relationship_description: 关系描述

        Returns:
            RelationExtraction: 关系抽取记录实例
        """
        from datetime import datetime
        created_at = datetime.now().isoformat()

        return cls(
            extraction_id=None,
            chunk_id=chunk_id,
            task_id=task_id,
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            relationship_description=relationship_description,
            created_at=created_at
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"RelationExtraction(id={self.extraction_id}, '{self.source_entity}' -> '{self.target_entity}')"


class ClaimExtraction(BaseModel):
    """事实陈述抽取记录数据结构"""
    extraction_id: int | None = Field(description="抽取记录ID，创建时为None", default=None)
    chunk_id: str = Field(description="章节块唯一标识符")
    task_id: str = Field(description="抽取任务唯一标识符")

    # 抽取结果字段
    claim_category: str = Field(description="事实类别")
    claim_subject: str = Field(description="事实主体")
    claim_content: str = Field(description="事实内容描述")

    # 时间戳
    created_at: str = Field(description="创建时间")

    @classmethod
    def create_extraction(
        cls,
        chunk_id: str,
        task_id: str,
        claim_category: str,
        claim_subject: str,
        claim_content: str
    ) -> "ClaimExtraction":
        """
        创建事实陈述抽取记录实例

        Args:
            chunk_id: 章节块唯一标识符
            task_id: 抽取任务唯一标识符
            claim_category: 事实类别
            claim_subject: 事实主体
            claim_content: 事实内容描述

        Returns:
            ClaimExtraction: 事实陈述抽取记录实例
        """
        from datetime import datetime
        created_at = datetime.now().isoformat()

        return cls(
            extraction_id=None,
            chunk_id=chunk_id,
            task_id=task_id,
            claim_category=claim_category,
            claim_subject=claim_subject,
            claim_content=claim_content,
            created_at=created_at
        )

    def __str__(self) -> str:
        """字符串表示"""
        return f"ClaimExtraction(id={self.extraction_id}, category='{self.claim_category}', subject='{self.claim_subject}')"


class ErClaimWorkResult(BaseModel):
    """ER-Claim工作单元执行结果"""
    chunk_id: str = Field(description="处理的章节块ID")
    task_id: str = Field(description="关联的任务ID")

    # 抽取结果
    entities: List[ErExtractEntity] = Field(default=[], description="提取的实体列表")
    relationships: List[ErExtractRelation] = Field(default=[], description="提取的关系列表")
    claims: List[ClaimExtractItem] = Field(default=[], description="提取的事实陈述列表")

    @classmethod
    def create_result(
        cls,
        chunk_id: str,
        task_id: str,
        entities: List[ErExtractEntity] | None = None,
        relationships: List[ErExtractRelation] | None = None,
        claims: List[ClaimExtractItem] | None = None
    ) -> "ErClaimWorkResult":
        """
        创建工作单元执行结果实例

        Args:
            chunk_id: 章节块ID
            task_id: 任务ID
            entities: 实体列表
            relationships: 关系列表
            claims: 事实列表

        Returns:
            ErClaimWorkResult: 执行结果实例
        """
        return cls(
            chunk_id=chunk_id,
            task_id=task_id,
            entities=entities or [],
            relationships=relationships or [],
            claims=claims or []
        )

    def __str__(self) -> str:
        """字符串表示"""
        return (f"ErClaimWorkResult(chunk_id='{self.chunk_id}', "
                f"entities={len(self.entities)}, relationships={len(self.relationships)}, claims={len(self.claims)})")