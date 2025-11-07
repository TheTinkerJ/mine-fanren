#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缺失章节分析器
执行章节提取，找到缺失章节，调用LLM分析
"""

import os
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from chapter_chunk_extractor_fanren_impl import ChapterChunkExtractor
from models import ChapterChunk


class MissingChapterAnalyzer:
    """缺失章节分析器"""

    # 提示词模板常量
    CHAPTER_DETECTION_PROMPT = """
-Goal-
给定前一章节的文本内容和目标章节号，识别可能属于目标章节的章节标题文本。

-Steps-
1. 在给定文本中搜索包含目标章节号"{target_chapter}"的所有文本行
2. 识别可能为章节标题的文本，包括但不限于：
   - 标准章节标题格式（如"第X章"）
   - 非标准或格式错误的章节标题
   - 包含章节号但缺少关键字段的文本
   - 可能的错别字或变体表达

3. 对于每个识别出的候选标题，提取以下信息：
   - title_text: 原始标题文本
   - confidence_score: 置信度评分 (1-10)
   - title_format: 标题格式类型 (standard/irregular/variant/potential)

4. 返回Python字典格式的配置项，格式为：
   "标题文本": ({target_chapter}, "volume_chapter")

-Output Requirements-
- 使用 **{record_delimiter}** 作为多个配置项的分隔符
- 当完成分析时输出 {completion_delimiter}
- 如果没有找到有效标题，输出：# 未找到明显的第{target_chapter}章标题

-Examples-
Example 1:
Target Chapter: 15
Text: ...第十四章 内容...第十五章 新的开始...第十六章 继续...
Output:
("chapter_title"{tuple_delimiter}第十五章 新的开始{tuple_delimiter}standard{tuple_delimiter}标准章节标题格式，置信度高){completion_delimiter}

Example 2:
Target Chapter: 23
Text: ...第廿二章 过渡...廿三章 突变...第24章 继续...
Output:
("chapter_title"{tuple_delimiter}廿三章 突变{tuple_delimiter}variant{tuple_delimiter}使用中文数字的非标准格式){completion_delimiter}

-Real Data-
Target Chapter: {target_chapter}
Text: {input_text}
Output:"""

    def __init__(self):
        """初始化分析器"""
        load_dotenv()
        self.llm = ChatOpenAI(
            model="kimi-k2-0905-preview",
            temperature=0.1,
        )

    def find_all_missing_chapters(self, novel_name: str, raw_text: str) -> List[tuple]:
        """
        找到所有缺失章节

        Args:
            novel_name: 小说名称
            raw_text: 原始文本

        Returns:
            List[tuple]: 缺失章节信息列表 [(缺失章节号, 前一章块), ...]
        """
        print("正在提取章节...")
        chunks = ChapterChunkExtractor.extract_chapter_chunks(novel_name, raw_text)

        print(f"共提取到 {len(chunks)} 个章节块")

        missing_chapters = []

        for i, chunk in enumerate(chunks):
            if chunk.token_count == 0:  # 缺失章节
                # 找到前一个非缺失章节
                prev_chunk = None
                for j in range(i - 1, -1, -1):
                    if chunks[j].token_count > 0:
                        prev_chunk = chunks[j]
                        break

                if prev_chunk:
                    missing_chapters.append((chunk.chapter_id, prev_chunk))
                    print(f"发现缺失章节: 第{chunk.chapter_id}章 (前一章: 第{prev_chunk.chapter_id}章)")
                else:
                    print(f"发现缺失章节: 第{chunk.chapter_id}章 (无前一章)")

        print(f"总共发现 {len(missing_chapters)} 个缺失章节")
        return missing_chapters

    def _format_prompt(self, template: str, **kwargs) -> str:
        """
        格式化提示词模板

        Args:
            template: 提示词模板
            **kwargs: 模板参数

        Returns:
            str: 格式化后的提示词
        """
        # 默认分隔符
        defaults = {
            'tuple_delimiter': '<|>',
            'record_delimiter': '<||>',
            'completion_delimiter': '<END>'
        }
        defaults.update(kwargs)

        return template.format(**defaults)

    def analyze_missing_chapter(self, missing_id: int, prev_chunk: ChapterChunk) -> str:
        """
        分析缺失章节

        Args:
            missing_id: 缺失章节号
            prev_chunk: 前一章块

        Returns:
            str: LLM分析结果
        """
        # 使用结构化提示词模板
        system_prompt = self._format_prompt(
            self.CHAPTER_DETECTION_PROMPT,
            target_chapter=missing_id,
            input_text=prev_chunk.content
        )

        # 用户提示词 - 提供上下文信息
        user_prompt = f"""分析任务：在给定的前一章节内容中识别第{missing_id}章的章节标题

## 上下文信息
- 目标章节: 第{missing_id}章
- 前一章节: 第{prev_chunk.chapter_id}章 {prev_chunk.chapter_title}
- 章节提取模式: volume_chapter (卷+章节模式)

## 输入文本
{prev_chunk.content}

请基于上述文本，识别可能属于第{missing_id}章的章节标题。"""

        print(f"正在调用LLM分析第{missing_id}章...")

        # 调用LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content # type: ignore

    def run_analysis(self, novel_file: str = "resources/ignored/1.txt", novel_name: str = "fanren"):
        """
        运行完整分析流程，处理所有缺失章节

        Args:
            novel_file: 小说文件路径
            novel_name: 小说名称
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

        # 找到所有缺失章节
        missing_chapters = self.find_all_missing_chapters(novel_name, raw_text)

        if not missing_chapters:
            print("没有发现缺失章节，无需分析")
            return None

        print("=" * 50)
        print("开始循环分析所有缺失章节...")
        print("=" * 50)

        all_results = []

        # 循环处理每个缺失章节
        for i, (missing_id, prev_chunk) in enumerate(missing_chapters, 1):
            print(f"\n[{i}/{len(missing_chapters)}] 正在分析第{missing_id}章...")

            # 调用LLM分析
            analysis_result = self.analyze_missing_chapter(missing_id, prev_chunk)

            # 保存结果
            all_results.append({
                'missing_id': missing_id,
                'prev_chapter_id': prev_chunk.chapter_id,
                'prev_chapter_title': prev_chunk.chapter_title,
                'analysis_result': analysis_result
            })

            print(f"第{missing_id}章分析完成")
            print("-" * 30)

        # 输出汇总结果
        print("\n" + "=" * 50)
        print("所有缺失章节分析汇总:")
        print("=" * 50)

        valid_configs = []
        for result in all_results:
            print(f"\n第{result['missing_id']}章 (前一章: 第{result['prev_chapter_id']}章):")
            print(f"分析结果: {result['analysis_result']}")

            # 检查是否找到了有效的配置项
            if not result['analysis_result'].startswith('# 未找到'):
                valid_configs.append(result['analysis_result'])

        # 输出最终配置建议
        if valid_configs:
            print("\n" + "=" * 50)
            print("可添加到SPECIAL_CHAPTER_MAPPING的配置项:")
            print("=" * 50)
            for config in valid_configs:
                print(config)
        else:
            print("\n" + "=" * 50)
            print("未找到任何可添加的配置项")
            print("=" * 50)

        return all_results


def main():
    """主函数"""
    analyzer = MissingChapterAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()