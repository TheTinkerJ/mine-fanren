#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Claim Extractor using LangChain 1.0 with MiniMax backend
Extract claims (factual statements) using LangChain with async/await support
"""

import os
import logging
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from src.imod.fanren_claim_extract_prompts import (
    FANREN_CLAIM_EXTRACTION_SYSTEM_TEMPLATE,
    FANREN_CLAIM_EXTRACTION_PROMPT_TEMPLATE
)
from src.imod.types import ClaimExtractItem, ClaimExtractResult, ErExtractEntity

# Configure logger
logger = logging.getLogger(__name__)


class FanrenClaimExtractor:
    """Async claim extraction processor using LangChain 1.0 with MiniMax backend"""

    def __init__(self):
        """Initialize claim extractor with environment variables"""
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

    async def extract_claims(
        self,
        textChunk: str,
        entities_info: str = ""
    ) -> ClaimExtractResult:
        """
        Extract claims (factual statements) from text chunk asynchronously

        Args:
            textChunk: Text content to extract claims from
            entities_info: Formatted entity information to reference during claim extraction

        Returns:
            ClaimExtractResult: Extraction result containing claims
        """
        try:
            # Build prompts using templates
            system_prompt = FANREN_CLAIM_EXTRACTION_SYSTEM_TEMPLATE.render()

            user_prompt = FANREN_CLAIM_EXTRACTION_PROMPT_TEMPLATE.render(
                entities_info=entities_info,
                input_text=textChunk
            )

            # Create messages for LangChain
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.info(f"Starting claim extraction")
            logger.debug(f"Text content length: {len(textChunk)} characters")

            # Call LLM asynchronously
            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            try:
                extraction_data = self.json_parser.parse(response.content)  # type: ignore
            except OutputParserException as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response.content}")
                return ClaimExtractResult(claims=[])

            # Build structured result
            claims = []
            for claim_data in extraction_data.get("claims", []):
                claim = ClaimExtractItem(
                    category=claim_data.get("category", ""),
                    subject=claim_data.get("subject", ""),
                    content=claim_data.get("content", "")
                )
                claims.append(claim)

            result = ClaimExtractResult(claims=claims)

            logger.info(
                f"Claim extraction completed successfully - "
                f"Claims: {len(claims)}"
            )

            return result

        except Exception as e:
            logger.error(
                f"Claim extraction failed - "
                f"Error: {str(e)}",
                exc_info=True
            )
            return ClaimExtractResult(claims=[])

    async def extract_from_chunks_batch(
        self,
        textChunks: list[str]
    ) -> list[ClaimExtractResult]:
        """
        Extract claims from multiple text chunks concurrently

        Args:
            textChunks: List of text chunks

        Returns:
            List of extraction results
        """
        import asyncio

        logger.info(f"Starting batch claim extraction for {len(textChunks)} text chunks")

        # Create tasks for concurrent processing
        tasks = [
            self.extract_claims(textChunk)
            for textChunk in textChunks
        ]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and log exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Text chunk {i} extraction failed: {result}")
                processed_results.append(ClaimExtractResult(claims=[]))
            else:
                processed_results.append(result)

        successful_count = sum(1 for r in processed_results if r.claims)
        logger.info(f"Batch extraction completed - {successful_count}/{len(textChunks)} chunks successful")

        return processed_results

    @staticmethod
    def format_entities_info(entities: list[ErExtractEntity]) -> str:
        """
        Format entity information for claim extraction (static method)

        Args:
            entities: List of entities to format

        Returns:
            str: Formatted entity information
        """
        if not entities:
            return "无已识别实体"

        entity_info = []
        for entity in entities:
            entity_info.append(f"- {entity.name} [{entity.category}]: {entity.desc}")

        return "\n".join(entity_info)