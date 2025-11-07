#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析缺失章节的启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 现在可以导入模块
from missing_chapter_analyzer import MissingChapterAnalyzer

def main():
    """主函数"""
    analyzer = MissingChapterAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()