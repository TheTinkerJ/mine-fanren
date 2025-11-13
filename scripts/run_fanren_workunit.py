#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行凡人小说文本切块WorkUnit的脚本
从项目根目录运行，负责正确设置Python路径并调用workunit
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入并运行workunit
from src.workunit.fanren_text_chunk_workunit import FanrenTextChunkWorkUnit

def main():
    """主函数"""
    # 默认配置
    novel_file = "resources/ignored/1.txt"
    novel_name = "fanren"

    # 检查文件是否存在
    if not Path(novel_file).exists():
        print(f"错误: 文件不存在 {novel_file}")
        print("请确保文件路径正确")
        return 1

    try:
        # 创建并运行工作单元
        workunit = FanrenTextChunkWorkUnit(novel_file, novel_name)
        processed_count = workunit.run()

        print(f"\n处理完成! 共处理了 {processed_count} 个章节")
        return 0

    except Exception as e:
        print(f"\n处理失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())