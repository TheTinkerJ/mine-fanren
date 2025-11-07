#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 命令行工具
用于查询和管理 ChapterChunk 数据
"""

import argparse
import sys
import os

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.store.sqlite_conn import get_sqlite_db
from src.store.sqlite_repo import ChapterChunkRepo


def query_chapter_content(novel_name: str, chapter_id: int):
    """
    查询并显示指定小说章节的内容

    Args:
        novel_name: 小说名称
        chapter_id: 章节ID
    """
    try:
        with get_sqlite_db() as db:
            conn = db.get_connection()

            # 使用批量查询方法，传入单个章节ID
            chunks = ChapterChunkRepo.get_chunks_by_chapter_ids(
                conn, novel_name, [chapter_id]
            )

            if not chunks:
                print(f"❌ 未找到小说 '{novel_name}' 的第 {chapter_id} 章")
                return

            chunk = chunks[chapter_id]

            # 显示章节信息
            print(f"📚 小说: {chunk.novel_name}")
            print(f"📖 第 {chunk.chapter_id} 章: {chunk.chapter_title}")
            print(f"📝 字符数: {chunk.char_count:,} | Token数: {chunk.token_count:,}")
            print(f"📍 位置: {chunk.pos_start}-{chunk.pos_end}")
            print("=" * 60)

            # 显示章节内容
            print(chunk.content)

    except Exception as e:
        print(f"❌ 查询失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SQLite 章节查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sqlite_cli.py -q fanren 1      # 查询《凡人修仙传》第1章
  python sqlite_cli.py -q "修仙" 5      # 查询小说《修仙》第5章
        """
    )

    # 查询参数
    parser.add_argument(
        '-q', '--query',
        nargs=2,
        metavar=('NOVEL', 'CHAPTER'),
        help='查询指定小说的章节内容 (小说名 章节号)'
    )

    args = parser.parse_args()

    if args.query:
        novel_name, chapter_id_str = args.query
        try:
            chapter_id = int(chapter_id_str)
            query_chapter_content(novel_name, chapter_id)
        except ValueError:
            print(f"❌ 错误: 章节号 '{chapter_id_str}' 必须是数字")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()