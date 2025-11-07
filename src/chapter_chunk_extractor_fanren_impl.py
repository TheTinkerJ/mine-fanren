#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节分块提取器实现
专门用于《凡人修仙传》小说章节分块提取
"""

from typing import List, Tuple, Dict, Optional
import re
import uuid

from .models import ChapterChunk
from .utils import count_tokens


class ChapterChunkExtractor:
    """章节块提取器"""

    # 章节标题模式
    CHAPTER_PATTERNS = [
        # 卷+章节模式：如 "第七卷纵横人界第一千一百三十章拦截"
        (r'^第([零一二三四五六七八九十百千万两\d]+)卷.*第([零一二三四五六七八九十百千万两\d]+)章', 'volume_chapter'),
        # 纯章节模式：如 "第1713章得丹"、"第一千七百一十四章甲士"
        (r'^第([零一二三四五六七八九十百千万两\d]+)章', 'chapter')
    ]

    # 排除规则（暂时置空，用于测试）
    EXCLUDE_PATTERNS = [
        # 暂时置空，用于测试基本章节识别效果
        # r'.*["\"「『].*["\"」』].*',  # 包含对话引号
        # r'.*(说道|回答道|喊道|想到).{5,}.*',  # 包含对话词汇
        # r'.{50,}',  # 过长的行
    ]

    @staticmethod
    def extract_chapter_chunks(novel_name: str, raw_text: str) -> List[ChapterChunk]:
        splitChunks:List[ChapterChunk] = ChapterChunkExtractor._extract_chapter_chunks(novel_name, raw_text)
        # 继续针对第一轮切
        return splitChunks

    @staticmethod
    def _extract_chapter_chunks(novel_name: str, raw_text: str) -> List[ChapterChunk]:
        """
        从原始文本提取章节块

        Args:
            novel_name: 小说名称
            raw_text: 原始文本内容

        Returns:
            List[ChapterChunk]: 章节块列表
        """
        if not raw_text or not raw_text.strip():
            return []

        # 1. 预处理
        lines = raw_text.split('\n')
        positions = ChapterChunkExtractor._calculate_text_positions(raw_text)

        # 2. 扫描章节标题
        chapter_lines = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) < 5:  # 章节标题至少5个字符
                continue

            is_valid, chapter_type, chapter_id, full_title = ChapterChunkExtractor._is_valid_chapter_title(line_stripped)
            if is_valid:
                chapter_lines.append((i, chapter_id, full_title))

        # 3. 创建章节块
        chunks = []
        for i, (line_num, chapter_id, title) in enumerate(chapter_lines):
            # 确定内容边界
            content_start = line_num + 1
            content_end = chapter_lines[i + 1][0] if i + 1 < len(chapter_lines) else len(lines)

            # 提取内容
            content = '\n'.join(lines[content_start:content_end])

            # 创建ChapterChunk
            chunk = ChapterChunkExtractor._create_chapter_chunk(
                novel_name, title, chapter_id, content,
                content_start, content_end - 1, positions
            )
            chunks.append(chunk)

        return chunks

    @staticmethod
    def _enhanced_chinese_to_number(chinese_str: str) -> int:
        """基于规则的中文数字转换算法"""
        # 中文数字字符映射
        digits = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '两': 2
        }

        # 单位映射
        units = {
            '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000
        }

        # 如果是阿拉伯数字，直接转换
        if chinese_str.isdigit():
            return int(chinese_str)

        # 清理输入
        chinese_str = chinese_str.strip()
        if not chinese_str:
            return 0

        # 移除所有的零，因为中文数字中零主要是占位作用
        chinese_str = chinese_str.replace('零', '')

        # 如果清空后没有字符，返回0
        if not chinese_str:
            return 0

        # 特殊情况：单个字
        if len(chinese_str) == 1:
            if chinese_str in digits:
                return digits[chinese_str]
            elif chinese_str in units:
                return units[chinese_str]
            else:
                return 0

        # 初始化变量
        result = 0     # 最终结果
        temp = 0       # 当前部分的结果

        i = 0
        n = len(chinese_str)

        while i < n:
            char = chinese_str[i]

            if char in digits:
                # 遇到数字，看看下一个字符是什么
                digit_value = digits[char]

                # 检查是否是数字+单位组合
                if i + 1 < n and chinese_str[i + 1] in units:
                    # 数字+单位
                    unit_value = units[chinese_str[i + 1]]
                    if unit_value >= 10000:  # 万、亿
                        # 大单位，先处理temp
                        result += temp
                        temp = digit_value * unit_value
                        result += temp
                        temp = 0
                    else:
                        # 小单位，直接计算
                        temp += digit_value * unit_value
                    i += 2  # 跳过下一个字符（单位）
                else:
                    # 单独的数字，加到temp
                    temp += digit_value
                    i += 1

            elif char in units:
                # 遇到单位
                unit_value = units[char]
                if unit_value >= 10000:  # 万、亿
                    # 大单位，处理temp
                    if temp == 0:
                        temp = 1
                    result += temp * unit_value
                    temp = 0
                else:
                    # 小单位（十、百、千）
                    if temp == 0:
                        temp = 1
                    temp = temp * unit_value
                i += 1

            else:
                # 不认识的字符，跳过
                i += 1
                continue

        # 最终结果 = 结果 + 剩余的temp
        result += temp
        return result

    @staticmethod
    def _is_valid_chapter_title(line: str) -> Tuple[bool, str, int, str]:
        """识别章节标题，返回 (是否有效, 章节类型, 章节编号, 完整标题)"""
        # 检查排除模式
        for pattern in ChapterChunkExtractor.EXCLUDE_PATTERNS:
            if re.search(pattern, line):
                return False, "", 0, ""

        # 检查章节模式
        for pattern, chapter_type in ChapterChunkExtractor.CHAPTER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                if chapter_type == 'volume_chapter':
                    # 卷+章节模式，提取章节编号
                    chapter_num_str = match.group(2)
                    chapter_num = ChapterChunkExtractor._enhanced_chinese_to_number(chapter_num_str)
                    return True, chapter_type, chapter_num, line
                else:
                    # 纯章节模式
                    chapter_num_str = match.group(1)
                    chapter_num = ChapterChunkExtractor._enhanced_chinese_to_number(chapter_num_str)
                    return True, chapter_type, chapter_num, line

        return False, "", 0, ""

    @staticmethod
    def _calculate_text_positions(text: str) -> Dict[int, int]:
        """计算每行在原文中的起始字符位置"""
        lines = text.split('\n')
        positions = {}
        current_pos = 0

        for i, line in enumerate(lines):
            positions[i] = current_pos
            current_pos += len(line) + 1  # +1 for newline

        return positions

    @staticmethod
    def _create_chapter_chunk(
        novel_name: str,
        title: str,
        chapter_id: int,
        content: str,
        line_start: int,
        line_end: int,
        positions: Dict[int, int]
    ) -> ChapterChunk:
        """创建ChapterChunk对象"""

        # 计算字符位置
        pos_start = positions.get(line_start, 0)
        pos_end = positions.get(line_end, pos_start) + len(content.split('\n')[-1])

        # 使用utils.count_tokens计算token数
        token_count = count_tokens(content)

        # 调用ChapterChunk.create_chunk创建对象
        return ChapterChunk.create_chunk(
            novel_name=novel_name,
            chapter_id=chapter_id,
            chapter_title=title,
            content=content,
            line_start=line_start,
            line_end=line_end,
            pos_start=pos_start,
            pos_end=pos_end,
            token_count=token_count
        )