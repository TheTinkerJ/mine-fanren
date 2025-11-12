#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Entity Extractor using LangChain 1.0 with MiniMax backend
Extract entities and relationships using LangChain with async/await support
"""

import os
import json
import time
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from ..models import ChapterChunk
from .fanren_er_extract_prompts import (
    FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE,
    FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE
)
from .types import ErExtractEntity, ErExtractRelation, ErExtractResult

# Configure logger
logger = logging.getLogger(__name__)


class FanrenERExtractorAgent:
    """Async entity extractor using LangChain 1.0 with MiniMax backend"""

    def __init__(self):
        """Initialize entity extractor with environment variables"""
        self.api_key = os.getenv("MINIMAX_OPENAI_API_KEY")
        self.base_url = os.getenv("MINIMAX_OPENAI_BASE_URL")
        self.model_name = os.getenv("MINIMAX_OPENAI_MODEL")

        if not self.api_key:
            raise ValueError("MINIMAX_OPENAI_API_KEY environment variable is required")

        if not self.base_url:
            raise ValueError("MINIMAX_OPENAI_BASE_URL environment variable is required")

        if not self.model_name:
            raise ValueError("MINIMAX_OPENAI_MODEL environment variable is required")

        # Initialize LangChain ChatOpenAI with MiniMax backend
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=0.1,
            timeout=30,
            model_kwargs={"reasoning_split": True}
        )

        # Initialize JSON output parser
        self.json_parser = JsonOutputParser()

    async def extract_entities_and_relations(
        self,
        chunk: ChapterChunk
    ) -> ErExtractResult:
        """
        Extract entities and relationships from chapter chunk asynchronously

        Args:
            chunk: Chapter chunk data

        Returns:
            ErExtractResult: Extraction result containing entities and relationships
        """
        start_time = time.time()

        try:
            # Build prompts using templates
            system_prompt = FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE.render()

            user_prompt = FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE.render(
                input_text=chunk.content
            )

            # Create messages for LangChain
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.info(f"Starting entity extraction for {chunk.novel_name} chapter {chunk.chapter_id}")
            logger.debug(f"Chunk content length: {len(chunk.content)} characters")

            # Call LLM asynchronously
            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            try:
                extraction_data = self.json_parser.parse(response.content)
            except OutputParserException as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response.content}")
                return ErExtractResult(entities=[], relationships=[])

            # Build structured result
            entities = []
            for entity_data in extraction_data.get("entities", []):
                entity = ErExtractEntity(
                    name=entity_data.get("name", ""),
                    category=entity_data.get("category", ""),
                    desc=entity_data.get("desc", "")
                )
                entities.append(entity)

            relationships = []
            for rel_data in extraction_data.get("relationships", []):
                relation = ErExtractRelation(
                    source=rel_data.get("source", ""),
                    target=rel_data.get("target", ""),
                    desc=rel_data.get("desc", "")
                )
                relationships.append(relation)

            result = ErExtractResult(
                entities=entities,
                relationships=relationships
            )

            processing_time = time.time() - start_time
            logger.info(
                f"Entity extraction completed successfully in {processing_time:.2f}s - "
                f"Entities: {len(entities)}, Relationships: {len(relationships)}"
            )

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Entity extraction failed after {processing_time:.2f}s - "
                f"Error: {str(e)}",
                exc_info=True
            )
            return ErExtractResult(entities=[], relationships=[])

    async def extract_from_chunks_batch(
        self,
        chunks: list[ChapterChunk]
    ) -> list[ErExtractResult]:
        """
        Extract entities from multiple chunks concurrently

        Args:
            chunks: List of chapter chunks

        Returns:
            List of extraction results
        """
        import asyncio

        logger.info(f"Starting batch entity extraction for {len(chunks)} chunks")

        # Create tasks for concurrent processing
        tasks = [
            self.extract_entities_and_relations(chunk)
            for chunk in chunks
        ]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and log exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {i} extraction failed: {result}")
                processed_results.append(ErExtractResult(entities=[], relationships=[]))
            else:
                processed_results.append(result)

        successful_count = sum(1 for r in processed_results if r.entities or r.relationships)
        logger.info(f"Batch extraction completed - {successful_count}/{len(chunks)} chunks successful")

        return processed_results


def create_async_extractor() -> FanrenERExtractorAgent:
    """
    Create async entity extractor instance

    Returns:
        FanrenERExtractorAgent: Extractor instance
    """
    return FanrenERExtractorAgent()


async def extract_from_chunk(chunk: ChapterChunk) -> ErExtractResult:
    """
    Convenience function: extract entities from a single chapter chunk asynchronously

    Args:
        chunk: Chapter chunk data

    Returns:
        ErExtractResult: Extraction result
    """
    extractor = create_async_extractor()
    return await extractor.extract_entities_and_relations(chunk)


async def extract_from_chunks_batch(chunks: list[ChapterChunk]) -> list[ErExtractResult]:
    """
    Convenience function: extract entities from multiple chunks asynchronously

    Args:
        chunks: List of chapter chunks

    Returns:
        List of extraction results
    """
    extractor = create_async_extractor()
    return await extractor.extract_from_chunks_batch(chunks)