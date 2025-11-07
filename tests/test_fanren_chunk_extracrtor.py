#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的章节提取测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chapter_chunk_extractor_fanren_impl import ChapterChunkExtractor


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

    # 打印结果
    for chunk in chunks:
        print(f"{chunk.chapter_id} ( {chunk.token_count} tokens): {chunk.chapter_title}")


if __name__ == "__main__":
    main()