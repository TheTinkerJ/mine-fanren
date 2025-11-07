#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含中文数字转换、词元计算等工具函数
"""
import tiktoken
import re

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    使用tiktoken计算文本的token数量

    Args:
        text: 要计算的文本
        encoding_name: 编码名称，默认为"cl100k_base"

    Returns:
        token数量
    """
    if not text:
        return 0

    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        # 如果编码失败，使用估算方法
        # 中文文本：1个字符 ≈ 1.5个token
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        estimated_tokens = int(chinese_chars * 1.5 + other_chars * 0.25)
        return estimated_tokens
