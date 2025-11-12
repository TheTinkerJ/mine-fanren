#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Entity Extractor using LangChain 1.0 with MiniMax backend
Extract entities and relationships using LangChain with async/await support
"""

import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from .fanren_er_extract_prompts import (
    FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE,
    FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE
)
from .types import ErExtractEntity, ErExtractRelation, ErExtractResult

# Configure logger
logger = logging.getLogger(__name__)


class FanrenEntityExtractor:
    """Async entity extraction processor using LangChain 1.0 with MiniMax backend"""

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

        # Initialize ChatOpenAI with MiniMax backend and reasoning_split support
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=SecretStr(self.api_key),
            base_url=self.base_url,
            temperature=0.1,
            timeout=60,
            extra_body={"reasoning_split": True},
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        # Initialize JSON output parser
        self.json_parser = JsonOutputParser()

    async def extract_entities_and_relations(
        self,
        textChunk: str
    ) -> ErExtractResult:
        """
        Extract entities and relationships from text chunk asynchronously

        Args:
            textChunk: Text content to extract entities and relationships from

        Returns:
            ErExtractResult: Extraction result containing entities and relationships
        """
        try:
            # Build prompts using templates
            system_prompt = FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE.render()

            user_prompt = FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE.render(
                input_text=textChunk
            )

            # Create messages for LangChain
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.info(f"Starting entity extraction")
            logger.debug(f"Text content length: {len(textChunk)} characters")

            # Call LLM asynchronously
            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            try:
                extraction_data = self.json_parser.parse(response.content)  # type: ignore
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

            logger.info(
                f"Entity extraction completed successfully - "
                f"Entities: {len(entities)}, Relationships: {len(relationships)}"
            )

            return result

        except Exception as e:
            logger.error(
                f"Entity extraction failed - "
                f"Error: {str(e)}",
                exc_info=True
            )
            return ErExtractResult(entities=[], relationships=[])

    async def extract_from_chunks_batch(
        self,
        textChunks: list[str]
    ) -> list[ErExtractResult]:
        """
        Extract entities from multiple text chunks concurrently

        Args:
            textChunks: List of text chunks

        Returns:
            List of extraction results
        """
        import asyncio

        logger.info(f"Starting batch entity extraction for {len(textChunks)} text chunks")

        # Create tasks for concurrent processing
        tasks = [
            self.extract_entities_and_relations(textChunk)
            for textChunk in textChunks
        ]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and log exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Text chunk {i} extraction failed: {result}")
                processed_results.append(ErExtractResult(entities=[], relationships=[]))
            else:
                processed_results.append(result)

        successful_count = sum(1 for r in processed_results if r.entities or r.relationships)
        logger.info(f"Batch extraction completed - {successful_count}/{len(textChunks)} chunks successful")

        return processed_results


def create_async_extractor() -> FanrenEntityExtractor:
    """
    Create async entity extractor instance

    Returns:
        FanrenEntityExtractor: Extractor instance
    """
    return FanrenEntityExtractor()


async def extract_from_text_chunk(textChunk: str) -> ErExtractResult:
    """
    Convenience function: extract entities from a single text chunk asynchronously

    Args:
        textChunk: Text content to extract entities from

    Returns:
        ErExtractResult: Extraction result
    """
    extractor = create_async_extractor()
    return await extractor.extract_entities_and_relations(textChunk)


async def extract_from_text_chunks_batch(textChunks: list[str]) -> list[ErExtractResult]:
    """
    Convenience function: extract entities from multiple text chunks asynchronously

    Args:
        textChunks: List of text chunks

    Returns:
        List of extraction results
    """
    extractor = create_async_extractor()
    return await extractor.extract_from_chunks_batch(textChunks)
