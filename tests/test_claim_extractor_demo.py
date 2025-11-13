#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fanren Claim Extractor Demo Test
简单的集成测试脚本，直观展示事实陈述提取效果
"""

import asyncio
import logging
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.imod.fanren_claim_extract_module import FanrenClaimExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_test_text():
    """创建测试用的文本数据"""
    test_content = """
    韩立服下筑基丹后，立刻盘膝坐下开始冲击筑基期。三个月后，他终于成功突破，从练气13层晋升为筑基初期修士。突破后，他发现丹田中凝聚出一颗金色的筑基道基。

    突破成功后，韩立决定前往血色禁地试炼，希望能够获得一些修炼资源。在禁地中，他遇到了同门师兄弟王蝉，两人因为争夺一株灵药而发生冲突。

    经过一番激战，韩立凭借新获得的筑基期修为和丰富的战斗经验，成功击败了王蝉，但也因此结下了仇怨。韩立获得了血莲草这株珍贵灵药，准备用来炼制丹药。

    在离开禁地时，韩立意外发现了一个古老的传送阵，据说可以通往上古秘境。他决定先返回宗门，做好充分准备后再来探索这个传送阵。
    """

    return test_content


async def test_single_text_extraction():
    """测试单个文本块的事实陈述提取"""
    logger.info("🚀 开始测试单个文本块事实陈述提取...")

    try:
        # 创建提取器实例
        claim_extractor = FanrenClaimExtractor()

        # 创建测试数据
        text_content = create_test_text()

        logger.info(f"📝 内容长度: {len(text_content)} 字符")
        logger.info("📄 原文内容:")
        logger.info("-" * 50)
        logger.info(text_content.strip())
        logger.info("-" * 50)

        # 模拟已识别的实体信息（手动创建测试数据）
        logger.info("🔍 使用预设的实体信息...")
        entities_info = """- 韩立 [character]: 修仙小说的主角，资质平凡但意志坚定
- 筑基丹 [item]: 用于冲击筑基境界的丹药
- 筑基初期 [state]: 修仙境界等级之一
- 血色禁地 [location]: 危险的试炼区域
- 血莲草 [item]: 珍贵的灵药
- 王蝉 [character]: 韩立的对手
- 上古秘境 [location]: 隐藏的古代传承之地
- 传送阵 [item]: 连接不同空间的法阵"""
        logger.info("📝 实体信息已准备")

        # 执行事实陈述提取（带实体信息）
        logger.info("🎯 基于实体信息提取事实陈述...")
        result = await claim_extractor.extract_claims(text_content, entities_info)

        # 显示提取结果
        logger.info("✅ 事实陈述提取完成!")
        logger.info(f"🎯 提取到 {len(result.claims)} 个事实陈述")

        # 详细显示事实陈述
        if result.claims:
            logger.info("\n📋 事实陈述列表:")
            for i, claim in enumerate(result.claims, 1):
                logger.info(f"{i}. [{claim.category}] {claim.subject}")
                logger.info(f"   内容: {claim.content}")

        return result

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return None


async def test_batch_extraction():
    """测试批量文本块的事实陈述提取"""
    logger.info("\n🚀 开始测试批量文本块事实陈述提取...")

    try:
        # 创建提取器实例
        extractor = FanrenClaimExtractor()

        # 创建多个测试文本块
        text_chunks = []

        # 文本块1
        content1 = "韩立突破至筑基期，成功凝聚筑基道基。他消耗了一颗筑基丹进行突破。"
        text_chunks.append(content1)

        # 文本块2
        content2 = "在血色禁地中，韩立与王蝉发生战斗，击败了对方并获得了血莲草，但也结下了仇怨。"
        text_chunks.append(content2)

        # 文本块3
        content3 = "韩立发现了一个通往上古秘境的传送阵，决定先回宗门准备再来探索。"
        text_chunks.append(content3)

        logger.info(f"📚 准备处理 {len(text_chunks)} 个文本块")

        # 执行批量提取
        results = await extractor.extract_from_chunks_batch(text_chunks)

        # 显示批量提取结果
        logger.info("✅ 批量提取完成!")

        total_claims = sum(len(result.claims) for result in results)
        logger.info(f"🎯 总计提取到 {total_claims} 个事实陈述")

        # 分块显示结果
        for i, (text_chunk, result) in enumerate(zip(text_chunks, results), 1):
            logger.info(f"\n📖 文本块 {i}")
            logger.info(f"   事实陈述数: {len(result.claims)}")

            if result.claims:
                logger.info("   事实: " + ", ".join([f"[{c.category}] {c.subject}" for c in result.claims]))

        return results

    except Exception as e:
        logger.error(f"❌ 批量测试失败: {e}")
        return None


async def main():
    """主测试函数"""
    logger.info("🧪 凡人事实陈述提取器 - 集成测试开始")
    logger.info("=" * 60)

    # 检查环境变量
    required_env = ["MINIMAX_OPENAI_API_KEY", "MINIMAX_OPENAI_BASE_URL", "MINIMAX_OPENAI_MODEL"]
    missing_env = [env for env in required_env if not os.getenv(env)]

    if missing_env:
        logger.error(f"❌ 缺少环境变量: {', '.join(missing_env)}")
        logger.error("请确保已配置以下环境变量:")
        for env in missing_env:
            logger.error(f"  - {env}")
        return

    logger.info("✅ 环境变量检查通过")

    # 执行测试
    try:
        # 测试1: 单个文本块
        result1 = await test_single_text_extraction()

        # 测试2: 批量文本块
        result2 = await test_batch_extraction()

        # 总结
        logger.info("\n" + "=" * 60)
        logger.info("🎉 集成测试完成!")


    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())