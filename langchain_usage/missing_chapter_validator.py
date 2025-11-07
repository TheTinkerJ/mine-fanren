#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缺失章节验证器
对空章节进行前后章节分析，让AI判断是否真的缺失
"""

import os
import sys
import argparse
from typing import List, Optional, Tuple, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 添加 src 目录到 Python 路径，以便导入依赖的模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chapter_chunk_extractor_fanren_impl import ChapterChunkExtractor
from models import ChapterChunk


class MissingChapterValidator:
    """缺失章节验证器"""

    # 章节验证提示词模板
    CHAPTER_VALIDATION_PROMPT = """
-Goal-
给定前后章节的文本内容，判断目标章节是否真的缺失内容，或者章节标题是否被错误识别。

-Steps-
1. 仔细分析前一章和后一章的内容：
   - 前一章：第{prev_chapter}章 {prev_title}
   - 目标章节：第{target_chapter}章（需要验证）
   - 后一章：第{next_chapter}章 {next_title}

2. 评估以下几个方面：
   - 前一章结尾是否正常，是否暗示了下一章的内容
   - 后一章开头是否与前一章节内容连贯
   - 前后章节之间是否存在明显的内容跳跃
   - 是否存在章节标题但内容为空的情况

3. 检查前一章内容中是否可能包含目标章节的标题：
   - 搜索包含"{target_chapter}"的文本
   - 识别可能的章节标题变体（如"第{target_chapter}章"的错别字或格式变化）
   - 检查是否有被误认为正文内容的章节标题

4. 判断结果分类：
   - MISSING: 章节确实缺失，前一章标题正确，需要为第{target_chapter}章找到正确的标题
   - FOUND_TITLE: 找到了第{target_chapter}章的标题，但内容被错误识别为空
   - NOT_MISSING: 章节没有缺失，前后章节内容连贯
   - UNCLEAR: 信息不足，无法确定

-Output Format-
输出格式如下：

判断结果: [MISSING/FOUND_TITLE/NOT_MISSING/UNCLEAR]

置信度: [1-10分]

详细分析:
[详细说明判断依据]

如果为FOUND_TITLE，请输出：
找到的标题: "标题文本" ({target_chapter}, "volume_chapter")

-Examples-
Example 1:
前一章: 第15章 激战之后
目标章节: 第16章
后一章: 第17章 新的开始
Output:
判断结果: MISSING
置信度: 9
详细分析: 前一章结尾正常结束，后一章明显是新开始的内容，中间缺少了第16章的内容。

Example 2:
前一章: 第20章 决战准备
目标章节: 第21章
后一章: 第22章 胜利归来
Output:
判断结果: FOUND_TITLE
置信度: 8
详细分析: 在前一章内容中发现了"第21章最终决战"的标题，但被错误识别为正文内容。
找到的标题: "第21章最终决战" (21, "volume_chapter")

-Real Data-
前一章标题: 第{prev_chapter}章 {prev_title}
前一章内容:
{prev_content}

目标章节: 第{target_chapter}章

后一章标题: 第{next_chapter}章 {next_title}
后一章内容:
{next_content}

Output:"""

    def __init__(self):
        """初始化验证器"""
        load_dotenv()
        self.llm = ChatOpenAI(
            model="MiniMax-M2",
            temperature=0.1,
        )

    def get_surrounding_chapters(self, chunks: List[ChapterChunk], missing_id: int) -> Tuple[Optional[ChapterChunk], Optional[ChapterChunk]]:
        """
        获取缺失章节的前后章节

        Args:
            chunks: 所有章节块列表
            missing_id: 缺失章节ID

        Returns:
            Tuple[Optional[ChapterChunk], Optional[ChapterChunk]]: (前一章块, 后一章块)
        """
        prev_chunk = None
        next_chunk = None

        # 找到前一个非空章节
        for i in range(len(chunks)):
            if chunks[i].chapter_id == missing_id:
                # 查找前一个非空章节
                for j in range(i - 1, -1, -1):
                    if chunks[j].token_count > 0:
                        prev_chunk = chunks[j]
                        break
                # 查找后一个非空章节
                for k in range(i + 1, len(chunks)):
                    if chunks[k].token_count > 0:
                        next_chunk = chunks[k]
                        break
                break

        return prev_chunk, next_chunk

    def validate_missing_chapter(self, chunks: List[ChapterChunk], missing_id: int) -> Dict[str, Any]:
        """
        验证缺失章节是否真的缺失

        Args:
            chunks: 所有章节块列表
            missing_id: 缺失章节ID

        Returns:
            Dict[str, Any]: 验证结果
        """
        prev_chunk, next_chunk = self.get_surrounding_chapters(chunks, missing_id)

        if not prev_chunk or not next_chunk:
            return {
                'missing_id': missing_id,
                'result': 'UNCLEAR',
                'confidence': 0,
                'analysis': '无法找到前后章节进行验证',
                'found_title': None,
                'prev_chunk': prev_chunk,
                'next_chunk': next_chunk
            }

        # 构建提示词
        system_prompt = self.CHAPTER_VALIDATION_PROMPT.format(
            target_chapter=missing_id,
            prev_chapter=prev_chunk.chapter_id,
            prev_title=prev_chunk.chapter_title,
            prev_content=prev_chunk.content,  # 限制长度
            next_chapter=next_chunk.chapter_id,
            next_title=next_chunk.chapter_title,
            next_content=next_chunk.content   # 限制长度
        )

        user_prompt = f"""请仔细分析前后章节内容，判断第{missing_id}章是否真的缺失。

前一章：第{prev_chunk.chapter_id}章 {prev_chunk.chapter_title}
后一章：第{next_chunk.chapter_id}章 {next_chunk.chapter_title}

请根据前后内容的连贯性和完整性进行判断。"""

        print(f"正在验证第{missing_id}章...")

        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        # 解析响应
        analysis_text = response.content

        # 提取关键信息
        result = self._parse_validation_result(analysis_text, missing_id)

        result['missing_id'] = missing_id
        result['prev_chunk'] = prev_chunk
        result['next_chunk'] = next_chunk
        result['full_analysis'] = analysis_text

        return result

    def _parse_validation_result(self, analysis_text: str, missing_id: int) -> Dict[str, Any]:
        """
        解析AI分析结果

        Args:
            analysis_text: AI返回的分析文本
            missing_id: 缺失章节ID

        Returns:
            Dict[str, Any]: 解析后的结果
        """
        lines = analysis_text.split('\n')

        result = {
            'result': 'UNCLEAR',
            'confidence': 0,
            'analysis': '',
            'found_title': None
        }

        current_field = None

        for line in lines:
            line = line.strip()

            if line.startswith('判断结果:'):
                result['result'] = line.split(':', 1)[1].strip()
            elif line.startswith('置信度:'):
                try:
                    confidence_str = line.split(':', 1)[1].strip()
                    # 提取数字
                    confidence = int(''.join(filter(str.isdigit, confidence_str)))
                    result['confidence'] = min(10, max(1, confidence))
                except:
                    result['confidence'] = 5
            elif line.startswith('详细分析:'):
                current_field = 'analysis'
                result['analysis'] = line.split(':', 1)[1].strip()
            elif line.startswith('找到的标题:'):
                try:
                    title_line = line.split(':', 1)[1].strip()
                    # 解析标题格式: "标题文本" (id, "type")
                    if '"' in title_line and '(' in title_line:
                        title_part = title_line.split('"')[1]
                        # 构建配置行
                        result['found_title'] = f'"{title_part}": ({missing_id}, "volume_chapter")'
                except:
                    pass
            elif current_field == 'analysis' and line:
                result['analysis'] += '\n' + line

        return result

    def validate_all_missing_chapters(self, novel_name: str, raw_text: str, max_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        验证缺失章节

        Args:
            novel_name: 小说名称
            raw_text: 原始文本
            max_count: 最大验证数量，None表示验证所有

        Returns:
            List[Dict[str, Any]]: 验证结果
        """
        print("正在提取章节...")
        chunks = ChapterChunkExtractor.extract_chapter_chunks(novel_name, raw_text)

        # 找出所有空章节
        missing_chapters = []
        for chunk in chunks:
            if chunk.token_count == 0:
                missing_chapters.append(chunk.chapter_id)

        print(f"发现 {len(missing_chapters)} 个空章节")

        # 限制验证数量
        if max_count is not None:
            missing_chapters = missing_chapters[:max_count]
            print(f"将验证前 {len(missing_chapters)} 个空章节")

        print("开始验证...")

        results = []

        for i, missing_id in enumerate(missing_chapters, 1):
            print(f"\n[{i}/{len(missing_chapters)}] 验证第{missing_id}章...")

            result = self.validate_missing_chapter(chunks, missing_id)
            results.append(result)

            print(f"结果: {result['result']} (置信度: {result['confidence']}/10)")
            if result['found_title']:
                print(f"找到标题: {result['found_title']}")

        return results

    def run_validation(self, novel_file: str = "resources/ignored/1.txt", novel_name: str = "fanren", max_count: Optional[int] = None):
        """
        运行完整的验证流程

        Args:
            novel_file: 小说文件路径
            novel_name: 小说名称
            max_count: 最大验证数量，None表示验证所有
        """
        print(f"读取小说文件: {novel_file}")

        # 读取小说文本
        try:
            with open(novel_file, 'r', encoding='gb18030') as f:
                raw_text = f.read()
        except UnicodeDecodeError:
            try:
                with open(novel_file, 'r', encoding='gbk') as f:
                    raw_text = f.read()
            except UnicodeDecodeError:
                with open(novel_file, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()

        print(f"文件读取完成，总字符数: {len(raw_text)}")
        print("=" * 50)

        # 验证缺失章节
        results = self.validate_all_missing_chapters(novel_name, raw_text, max_count)

        # 输出汇总结果
        print("\n" + "=" * 50)
        print("缺失章节验证汇总:")
        print("=" * 50)

        # 统计各种结果
        stats = {
            'MISSING': 0,
            'FOUND_TITLE': 0,
            'NOT_MISSING': 0,
            'UNCLEAR': 0
        }

        found_configs = []

        for result in results:
            print(f"\n第{result['missing_id']}章:")
            print(f"  判断结果: {result['result']}")
            print(f"  置信度: {result['confidence']}/10")
            print(f"  分析: {result['analysis'][:100]}...")

            stats[result['result']] += 1

            if result['found_title']:
                found_configs.append(result['found_title'])
                print(f"  找到的标题: {result['found_title']}")

        # 输出统计结果
        print("\n" + "=" * 50)
        print("验证统计:")
        print("=" * 50)
        for result_type, count in stats.items():
            print(f"{result_type}: {count} 个")

        # 输出找到的标题配置
        if found_configs:
            print("\n" + "=" * 50)
            print("可添加到SPECIAL_CHAPTER_MAPPING的配置项:")
            print("=" * 50)
            for config in found_configs:
                print(config)

        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='缺失章节验证器')
    parser.add_argument('--file', '-f', default="resources/ignored/1.txt",
                       help='小说文件路径 (默认: resources/ignored/1.txt)')
    parser.add_argument('--name', '-n', default="fanren",
                       help='小说名称 (默认: fanren)')
    parser.add_argument('--count', '-c', type=int,
                       help='验证的章节数量 (默认: 验证所有)')

    args = parser.parse_args()

    validator = MissingChapterValidator()
    validator.run_validation(
        novel_file=args.file,
        novel_name=args.name,
        max_count=args.count
    )


if __name__ == "__main__":
    main()