#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的章节提取测试
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from rmod.fanran_chapter_chunk_module import ChapterChunkExtractor


def main():
    # 加载文件
    file_path = "resources/ignored/1.txt"

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return

    # 尝试不同的编码
    encodings = ['gb18030', 'gbk', 'utf-8']
    raw_text = None

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                raw_text = f.read()
            print(f"使用编码 {encoding} 成功读取文件")
            break
        except Exception as e:
            print(f"编码 {encoding} 失败: {e}")
            continue

    if raw_text is None:
        print("所有编码都失败，无法读取文件")
        return

    # 提取章节
    chunks = ChapterChunkExtractor.extract_chapter_chunks("fanren", raw_text)

    # 统计和打印空章节
    empty_chapters = []
    total_chapters = 0

    for chunk in chunks:
        total_chapters += 1
        if chunk.token_count == 0:  # 空章节
            empty_chapters.append(chunk)

    print(f"总章节数: {total_chapters}")
    print(f"空章节数: {len(empty_chapters)}")
    print(f"有效章节数: {total_chapters - len(empty_chapters)}")
    print("=" * 50)
    print("空章节列表:")
    print("=" * 50)

    for chunk in empty_chapters:
        print(f"{chunk.chapter_id} ( 0 tokens): {chunk.chapter_title}")

    if not empty_chapters:
        print("没有发现空章节！")


if __name__ == "__main__":
    main()