#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-Claim工作单元
集成实体关系抽取和事实抽取模块，专注于模块协调
"""

import logging

from src.models import ErClaimWorkResult, ChapterChunk, ChapterChunkTask
from src.imod.fanren_er_extract_module import FanrenEntityExtractor
from src.imod.fanren_claim_extract_module import FanrenClaimExtractor

# Configure logger
logger = logging.getLogger(__name__)


class ERClaimWorkUnit:
    """ER-Claim工作单元，负责协调实体关系抽取和事实抽取模块"""

    def __init__(self):
        """初始化工作单元"""
        # 初始化智能模块
        self.entity_extractor = FanrenEntityExtractor()
        self.claim_extractor = FanrenClaimExtractor()

    async def extract(
        self,
        chunk: ChapterChunk,
        task: ChapterChunkTask
    ) -> ErClaimWorkResult:
        """
        从章节块中提取实体、关系和事实

        Args:
            chunk: 章节块对象
            task: 任务对象

        Returns:
            ErClaimWorkResult: 抽取结果
        """
        logger.info(f"开始文本抽取: chunk_id={chunk.chunk_id}, task_id={task.task_id}")

        # 执行实体关系抽取
        logger.debug("执行实体关系抽取...")
        er_result = await self.entity_extractor.extract_entities_and_relations(chunk.content)
        entities = er_result.entities
        relationships = er_result.relationships
        logger.debug(f"实体关系抽取完成: {len(entities)}个实体, {len(relationships)}个关系")

        # 如果没有识别到实体，跳过事实抽取
        if not entities:
            logger.warning(f"未识别到任何实体，跳过事实抽取: chunk_id={chunk.chunk_id}")
            claims = []
        else:
            # 执行事实抽取
            logger.debug("执行事实抽取...")
            # 将已提取的实体信息传递给事实抽取模块
            entities_info = "\n".join([
                f"- {entity.name} ({entity.category})"
                for entity in entities
            ])
            claim_result = await self.claim_extractor.extract_claims(chunk.content, entities_info)
            claims = claim_result.claims
            logger.debug(f"事实抽取完成: {len(claims)}个事实")

        # 创建并返回结果
        result = ErClaimWorkResult.create_result(
            chunk_id=chunk.chunk_id,
            task_id=task.task_id,
            entities=entities,
            relationships=relationships,
            claims=claims
        )

        logger.info(f"文本抽取完成: {len(result.entities)}个实体, {len(result.relationships)}个关系, {len(result.claims)}个事实")
        return result

    def __str__(self) -> str:
        """字符串表示"""
        return "ERClaimWorkUnit()"