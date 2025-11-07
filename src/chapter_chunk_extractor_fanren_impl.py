#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节分块提取器实现
专门用于《凡人修仙传》小说章节分块提取
"""

from typing import List, Tuple, Dict, Optional
import re
import uuid

from models import ChapterChunk
from utils import count_tokens


class ChapterChunkExtractor:
    """章节块提取器"""

    # 特殊章节转换配置：badcase处理
    # 格式: {识别文本: (章节号, 章节类型)}
    SPECIAL_CHAPTER_MAPPING = {
        "四百五十五章意外频生": (455, "volume_chapter"),
        "第六卷通天灵宝随风掩形": (986, "volume_chapter"),
        "第一干一百一十八章空间神通": (1118, "volume_chapter"),
        "初入灵界第一千二百八十七章传承珠": (1287, "volume_chapter"),
        "九卷灵界百族第一千六百零九章出手": (1609, "volume_chapter"),
        "第一千六百九十六收山": (1696, "volume_chapter"),
        "一千七百零九章屏风、金鼎": (1709, "volume_chapter"),
        "1761第十卷魔界之战第一千七百六十一章真血隐忧": (1761, "volume_chapter"),
        "第十卷魔界之战一千八百零五章一抓,一拳,一掌": (1805, "volume_chapter"),
        "第十卷魔界之战1875": (1875, "volume_chapter"),
        "第十卷魔界之战1875": (1876, "volume_chapter"),
        "第十卷魔界之战人魔之战（二）": (1883, "volume_chapter"),
        "第十卷魔界之战人魔之战（二）": (1884, "volume_chapter"),
        "第十卷魔界之战一千九百零六章": (1906, "volume_chapter"),
        "第十卷魔界之战一千九百五十章狼狈": (1950, "volume_chapter"),
        "第十卷魔界之战一千九百七十一章獠影": (1971, "volume_chapter"),
        "第十卷魔界之战七杀血煞和黑骨魔虫": (2036, "volume_chapter"),
        "第十卷魔界之战第两千五十五章三魔害": (2055, "volume_chapter"),
        "十卷魔界之战第两千九十三章参天造化露": (2093, "volume_chapter"),
        "第十一卷真仙降世两千一百八十章黑白雷球": (2180, "volume_chapter"),
        "第十一卷真仙降世两千一百八十章黑白雷球": (2181, "volume_chapter"),
        "第十一卷真仙降世两千一百八十章黑白雷球": (2182, "volume_chapter"),
        "第十一卷真仙降世两千两百零八章天书阁": (2208, "volume_chapter"),
        "第十一卷真仙降世两千两百零八章天书阁": (2208, "volume_chapter"),
        "第十一卷真仙降世第两千两百零九章": (2209, "volume_chapter"),
        "一千百八零八": (1808, "volume_chapter"),
        "第十一卷真仙降世第两千三白三十七章八鬼噬佛图": (2337, "volume_chapter"),
        "第十一卷真仙降世第两千两百六十三四章乌龙": (2264, "volume_chapter"),
        "第十一卷真仙降世两千三百零六章黄元子": (2306, "volume_chapter"),
        "十一卷真仙降世第两千三百八十五章天地二阵": (2385, "volume_chapter"),
        "第十一卷真仙降世第两千三百一十二章青元之劫": (2311, "volume_chapter"),
        # 可以在这里添加更多特殊badcase
        # 例如：
        # "两千三百四十五": (2345, "chapter"),
        # "九百九十九": (999, "chapter"),
    }

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
        splitChunks: List[ChapterChunk] = ChapterChunkExtractor._extract_chapter_chunks(novel_name, raw_text)
        # 针对 _extract_chapter_chunks 的切块
        # 我们做一下块清洗的工作
        # 两个内容
        # 1. 重复章节的合并，合并策略: 保留 tokens 大的那个
        # 2. 丢失章节的记录 构造空内容的 ChapterChunk
        cleaned_chunks = ChapterChunkExtractor._clean_split_chunks(splitChunks, novel_name)
        return cleaned_chunks

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

        # 特殊badcase处理：检查特殊章节转换配置
        for badcase_text, (chapter_num, chapter_type) in ChapterChunkExtractor.SPECIAL_CHAPTER_MAPPING.items():
            if badcase_text in line:
                return True, chapter_type, chapter_num, line

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

    @staticmethod
    def _clean_split_chunks(chunks: List[ChapterChunk], novel_name: str) -> List[ChapterChunk]:
        """
        清洗章节块，处理重复章节合并和丢失章节补全

        Args:
            chunks: 原始章节块列表
            novel_name: 小说名称

        Returns:
            List[ChapterChunk]: 清洗后的章节块列表
        """
        if not chunks:
            return []

        # 1. 重复章节的合并，合并策略: 保留 tokens 大的那个
        # 使用字典来去重，key为chapter_id，value为ChapterChunk
        chapter_dict: Dict[int, ChapterChunk] = {}

        for chunk in chunks:
            existing_chunk = chapter_dict.get(chunk.chapter_id)
            if existing_chunk is None:
                # 没有重复，直接添加
                chapter_dict[chunk.chapter_id] = chunk
            else:
                # 有重复，保留tokens多的那个
                if chunk.token_count > existing_chunk.token_count:
                    chapter_dict[chunk.chapter_id] = chunk

        # 2. 丢失章节的记录 构造空内容的 ChapterChunk
        # 找出所有存在的章节ID
        existing_ids = sorted(chapter_dict.keys())

        if not existing_ids:
            return []

        min_id, max_id = min(existing_ids), max(existing_ids)

        # 找出丢失的章节ID
        missing_ids = []
        for chapter_id in range(min_id, max_id + 1):
            if chapter_id not in chapter_dict:
                missing_ids.append(chapter_id)

        # 为丢失的章节构造空内容的ChapterChunk
        for missing_id in missing_ids:
            empty_chunk = ChapterChunk.create_chunk(
                novel_name=novel_name,
                chapter_id=missing_id,
                chapter_title=f"第{missing_id}章",
                content="",
                line_start=0,
                line_end=0,
                pos_start=0,
                pos_end=0,
                token_count=0
            )
            chapter_dict[missing_id] = empty_chunk

        # 3. 按章节ID排序返回
        cleaned_chunks = [chapter_dict[chapter_id] for chapter_id in sorted(chapter_dict.keys())]

        return cleaned_chunks