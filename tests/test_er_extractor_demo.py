#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fanren ER Extractor Demo Test
简单的集成测试脚本，直观展示实体提取效果
"""

import asyncio
import logging
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from imod.fanren_er_extract_mod import FanrenEntityExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_test_text():
    """创建测试用的文本数据"""
    test_content = """
    韩立在七玄门中遇到了自己的第一个师傅墨大夫，墨大夫传授了他长春功，帮助他踏上了修仙之路。
    后来韩立加入了黄枫谷，在那里他修炼了青元剑诀，并获得了掌天瓶这个神秘的法宝。
    在黄枫谷中，韩立还认识了师姐柳玉，两人一起参加了宗门的试炼。
    韩立凭借掌天瓶的能力，在修炼方面进步神速，很快成为了内门弟子。
    """

    return test_content


async def test_single_text_extraction():
    """测试单个文本块的实体提取"""
    logger.info("🚀 开始测试单个文本块实体提取...")

    try:
        # 创建提取器实例
        extractor = FanrenEntityExtractor()

        # 创建测试数据
        text_content = create_test_text()

        logger.info(f"📝 内容长度: {len(text_content)} 字符")
        logger.info("📄 原文内容:")
        logger.info("-" * 50)
        logger.info(text_content.strip())
        logger.info("-" * 50)

        # 执行实体提取
        result = await extractor.extract_entities_and_relations(text_content)

        # 显示提取结果
        logger.info("✅ 实体提取完成!")
        logger.info(f"🎯 提取到 {len(result.entities)} 个实体")
        logger.info(f"🔗 提取到 {len(result.relationships)} 个关系")

        # 详细显示实体
        if result.entities:
            logger.info("\n📋 实体列表:")
            for i, entity in enumerate(result.entities, 1):
                logger.info(f"{i}. {entity.name} [{entity.category}]")
                logger.info(f"   描述: {entity.desc}")

        # 详细显示关系
        if result.relationships:
            logger.info("\n🔗 关系列表:")
            for i, relation in enumerate(result.relationships, 1):
                logger.info(f"{i}. {relation.source} → {relation.target}")
                logger.info(f"   关系: {relation.desc}")

        return result

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return None


async def test_batch_extraction():
    """测试批量文本块的实体提取"""
    logger.info("\n🚀 开始测试批量文本块实体提取...")

    try:
        # 创建提取器实例
        extractor = FanrenEntityExtractor()

        # 创建多个测试文本块
        text_chunks = []

        # 文本块1
        content1 = "韩立在七玄门遇到了墨大夫，学习了长春功。墨大夫是韩立的第一个师傅。"
        text_chunks.append(content1)

        # 文本块2
        content2 = "韩立后来加入了黄枫谷，在那里修炼了青元剑诀。他还获得了掌天瓶这个神秘法宝。"
        text_chunks.append(content2)

        logger.info(f"📚 准备处理 {len(text_chunks)} 个文本块")

        # 执行批量提取
        results = await extractor.extract_from_chunks_batch(text_chunks)

        # 显示批量提取结果
        logger.info("✅ 批量提取完成!")

        total_entities = sum(len(result.entities) for result in results)
        total_relationships = sum(len(result.relationships) for result in results)

        logger.info(f"🎯 总计提取到 {total_entities} 个实体")
        logger.info(f"🔗 总计提取到 {total_relationships} 个关系")

        # 分块显示结果
        for i, (text_chunk, result) in enumerate(zip(text_chunks, results), 1):
            logger.info(f"\n📖 文本块 {i}")
            logger.info(f"   实体数: {len(result.entities)}, 关系数: {len(result.relationships)}")

            if result.entities:
                logger.info("   实体: " + ", ".join([f"{e.name}[{e.category}]" for e in result.entities]))
            if result.relationships:
                logger.info("   关系: " + ", ".join([f"{r.source}→{r.target}" for r in result.relationships]))

        return results

    except Exception as e:
        logger.error(f"❌ 批量测试失败: {e}")
        return None


async def main():
    """主测试函数"""
    logger.info("🧪 凡人实体关系提取器 - 集成测试开始")
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

        # 测试2: 批量处理
        result2 = await test_batch_extraction()

        # 总结
        logger.info("\n" + "=" * 60)
        logger.info("🎉 集成测试完成!")

        if result1 and result2:
            logger.info("✅ 所有测试通过")
        else:
            logger.info("⚠️  部分测试失败，请检查日志")

    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())