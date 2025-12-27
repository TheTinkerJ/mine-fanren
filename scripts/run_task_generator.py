#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行任务生成器
"""

# 添加项目根目录到Python路径
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("🚀 任务生成器启动")
    print("=" * 30)

    try:
        # 导入工作单元
        from src.workunit import FanrenTaskGeneratorWorkUnit
        print("✓ 导入工作单元成功")

        # 创建任务生成器
        task_generator = FanrenTaskGeneratorWorkUnit()
        print("✓ 创建任务生成器成功")

        # 生成任务
        print("\n📋 开始生成任务...")
        tasks = task_generator.generate_pending_tasks("erc", limit=10)

        print(f"✅ 成功生成 {len(tasks)} 个任务")

        if tasks:
            print("\n前3个任务示例:")
            for i, task in enumerate(tasks[:3]):
                print(f"  {i+1}. ID: {task.task_id[:8]}... 类型: {task.task_type}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n💡 提示:")
        print("  1. 确保在项目根目录运行")
        print("  2. 确保数据库文件存在: resources/ignored/sqlite.db")
        print("  3. 确保安装依赖: python3 scripts/install_deps.py")

if __name__ == "__main__":
    main()