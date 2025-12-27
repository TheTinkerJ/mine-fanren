#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键安装项目依赖
"""

import subprocess
import sys

def install_deps():
    print("📦 开始安装项目依赖...")

    deps = [
        "pydantic",
        "python-dotenv",
        "langchain",
        "langchain-openai",
    ]

    for dep in deps:
        print(f"  安装 {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"  ✅ {dep} 安装成功")
        except subprocess.CalledProcessError:
            print(f"  ❌ {dep} 安装失败")

    print("\n🎉 依赖安装完成!")
    print("现在可以运行: python3 scripts/run_task_generator.py")

if __name__ == "__main__":
    install_deps()