#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow 命令行工具
用于执行各种数据处理工作流
"""

import argparse
import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.store.sqlite_conn import get_sqlite_db
from src.store.sqlite_repo import ChapterChunkRepo
from src.chapter_chunk_extractor_fanren_impl import ChapterChunkExtractor
from src.models import ChapterChunk


def process_chapter_chunks(file_path: str, encoding: str):
    """
    处理章节分块工作流：加载文档 -> 分块 -> 存储到 SQLite

    Args:
        file_path: 文档文件路径
        encoding: 文件编码格式
    """
    try:
        print(f"📁 开始处理文件: {file_path}")
        print(f"🔤 编码格式: {encoding}")

        # 1. 检查文件是否存在
        full_path = os.path.join(project_root, file_path)
        if not os.path.exists(full_path):
            print(f"❌ 文件不存在: {full_path}")
            return

        # 2. 加载文档内容
        print(f"📖 正在加载文档...")
        with open(full_path, 'r', encoding=encoding) as f:
            content = f.read()

        print(f"✅ 文档加载成功，总字符数: {len(content):,}")

        # 3. 执行章节分块
        print(f"🔧 开始章节分块处理...")
        extractor = ChapterChunkExtractor()

        # 需要提供小说名称，从文件名推断
        novel_name = "fanren"  # 可以根据需要修改
        chunks = extractor.extract_chapter_chunks(novel_name, content)
        print(f"✅ 分块完成，共生成 {len(chunks)} 个章节块")

        # 4. 批量存储到 SQLite 数据库
        print(f"💾 开始批量存储到 SQLite 数据库...")

        with get_sqlite_db() as db:
            conn = db.get_connection()

            # 使用批量 UPSERT 操作存储所有章节块
            processed_count = ChapterChunkRepo.upsert_chunks(conn, chunks)

            # 提交事务
            conn.commit()

        print(f"✅ 批量存储完成！")
        print(f"📊 处理统计:")
        print(f"   - 总章节数: {len(chunks)}")
        print(f"   - 成功处理: {processed_count}")
        print(f"   - 总字符数: {sum(chunk.char_count for chunk in chunks):,}")
        print(f"   - 总Token数: {sum(chunk.token_count for chunk in chunks):,}")

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Workflow 工作流工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python workflow_cli.py -m chapter_chunk -f resources/ignored/1.txt gb18030
  python workflow_cli.py -m chapter_chunk -f data/novel.txt utf-8
        """
    )

    # 工作流模块参数
    parser.add_argument(
        '-m', '--module',
        required=True,
        choices=['chapter_chunk'],
        help='选择要执行的工作流模块'
    )

    # 文件参数
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='输入文件路径（相对于项目根目录）'
    )

    # 编码参数
    parser.add_argument(
        'encoding',
        help='文件编码格式（如：gb18030, utf-8, gbk等）'
    )

    args = parser.parse_args()

    if args.module == 'chapter_chunk':
        process_chapter_chunks(args.file, args.encoding)
    else:
        print(f"❌ 未知的工作流模块: {args.module}")
        sys.exit(1)


if __name__ == '__main__':
    main()