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

from imod.fanren_er_extract_module import FanrenEntityExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_test_text():
    """创建测试用的文本数据"""
    test_content = """
二愣子睁大着双眼，直直望着茅草和烂泥糊成的黑屋顶，身上盖着的旧棉被，已呈深黄色，看不出原来的本来面目，还若有若无的散着淡淡的霉味。

在他身边紧挨着的另一人，是二哥韩铸，酣睡的十分香甜，从他身上不时传来轻重不一的阵阵打呼声。

离床大约半丈远的地方，是一堵黄泥糊成的土墙，因为时间过久，墙壁上裂开了几丝不起眼的细长口子，从这些裂纹中，隐隐约约的传来韩母唠唠叨叨的埋怨声，偶尔还掺杂着韩父，抽旱烟杆的“啪嗒”“啪嗒”吸允声。

二愣子缓缓的闭上已有些涩的双目，迫使自己尽早进入深深的睡梦中。他心里非常清楚，再不老实入睡的话，明天就无法早起些了，也就无法和其他约好的同伴一起进山拣干柴。

二愣子姓韩名立，这么像模像样的名字,他父母可起不出来，这是他父亲用两个粗粮制成的窝头，求村里老张叔给起的名字。

老张叔年轻时，曾经跟城里的有钱人当过几年的伴读书童，是村里唯一认识几个字的读书人，村里小孩子的名字，倒有一多半是他给起的。

韩立被村里人叫作“二愣子”，可人并不是真愣真傻，反而是村中屈一指的聪明孩子，但就像其他村中的孩子一样，除了家里人外，他就很少听到有人正式叫他名字“韩立”，倒是“二愣子”“二愣子”的称呼一直伴随至今。

而之所以被人起了个“二愣子”的绰号，也只不过是因为村里已有一个叫“愣子”的孩子了。

这也没啥，村里的其他孩子也是“狗娃”“二蛋”之类的被人一直称呼着，这些名字也不见得比“二愣子”好听了哪里去。

因此，韩立虽然并不喜欢这个称呼，但也只能这样一直的自我安慰着。

韩立外表长得很不起眼，皮肤黑黑的，就是一个普通的农家小孩模样。但他的内心深处，却比同龄人早熟了许多，他从小就向往外面世界的富饶繁华，梦想有一天，他能走出这个巴掌大的村子，去看看老张叔经常所说的外面世界。

当韩立的这个想法，一直没敢和其他人说起过。否则，一定会使村里人感到愕然，一个乳臭未干的小屁孩，竟然会有这么一个大人也不敢轻易想的念头。要知道，其他同韩立差不多大的小孩，都还只会满村的追鸡摸狗，更别说会有离开故土，这么一个古怪的念头。

韩立一家七口人，有两个兄长，一个姐姐，还有一个小妹，他在家里排行老四，今年刚十岁，家里的生活很清苦，一年也吃不上几顿带荤腥的饭菜，全家人一直在温饱线上徘徊着。

此时的韩立，正处于迷迷糊糊，似睡未睡之间，恼中还一直残留着这样的念头：上山时，一定要帮他最疼爱的妹妹，多拣些她最喜欢吃的红浆果。

第二天中午时分，当韩立顶着火辣辣的太阳，背着半人高的木柴堆，怀里还揣着满满一布袋浆果，从山里往家里赶的时侯，并不知道家中已来了一位，会改变他一生命运的客人。

这位贵客，是跟他血缘很近的一位至亲，他的亲三叔。

听说，在附近一个小城的酒楼，给人当大掌柜，是他父母口中的大能人。韩家近百年来，可能就出了三叔这么一位有点身份的亲戚。

韩立只在很小的时侯，见过这位三叔几次。他大哥在城里给一位老铁匠当学徒的工作，就是这位三叔给介绍的，这位三叔还经常托人给他父母捎带一些吃的用的东西，很是照顾他们一家，因此韩立对这位三叔的印像也很好，知道父母虽然嘴里不说，心里也是很感激的。

大哥可是一家人的骄傲，听说当铁匠的学徒，不但管吃管住，一个月还有三十个铜板拿，等到正式出师被人雇用时，挣的钱可就更多了。

每当父母一提起大哥，就神采飞扬，像换了一个人一样。韩立年龄虽小，也羡慕不已，心目最好的工作也早早就有了，就是给小城里的哪位手艺师傅看上，收做学徒，从此变成靠手艺吃饭的体面人。

所以当韩立见到穿着一身崭新的缎子衣服，胖胖的圆脸，留着一撮小胡子的三叔时，心里兴奋极了。

把木柴在屋后放好后，便到前屋腼腆的给三叔见了个礼，乖乖的叫了声：“三叔好”，就老老实实的站在一边，听父母同三叔聊天。

三叔笑眯眯的望着韩立，打量着他一番，嘴里夸了他几句“听话”“懂事”之类的话，然后就转过头，和他父母说起这次的来意。

韩立虽然年龄尚小，不能完全听懂三叔的话，但也听明白了大概的意思。

原来三叔工作的酒楼，属于一个叫“七玄门”的江湖门派所有，这个门派有外门和内门之分，而前不久，三叔才正式成为了这个门派的外门弟子，能够推举7岁到12岁的孩童去参加七玄门招收内门弟子的考验。

五年一次的“七玄门”招收内门弟子测试，下个月就要开始了。这位有着几分精明劲自己尚无子女的三叔，自然想到了适龄的韩立。

一向老实巴交的韩父，听到“江湖”“门派”之类的从未听闻过的话，心里有些犹豫不决拿不定主意。便一把拿起旱烟杆，“吧嗒”“吧嗒”的狠狠抽了几口，就坐在那里，一声不吭。

在三叔嘴里，“七玄门”自然是这方圆数百里内，了不起的、数一数二的大门派。

只要成为内门弟子，不但以后可以免费习武吃喝不愁，每月还能有一两多的散银子零花。而且参加考验的人，即使未能入选也有机会成为像三叔一样的外门人员，专门替“七玄门”打理门外的生意。

当听到有可能每月有一两银子可拿，还有机会成为和三叔一样的体面人，韩父终于拿定了主意，答应了下来。

三叔见到韩父应承了下来，心里很是高兴。又留下几两银子，说一个月后就来带韩立走，在这期间给韩立多做点好吃的，给他补补身子，好应付考验。随后三叔和韩父打声招呼，摸了摸韩立的头，出门回城了。

韩立虽然不全明白三叔所说的话，但可以进城能挣大钱还是明白的。

一直以来的愿望，眼看就有可能实现，他一连好几个晚上兴奋的睡不着觉。

三叔在一个多月后，准时的来到村中，要带韩立走了，临走前韩父反复嘱咐韩立，做人要老实，遇事要忍让，别和其他人起争执，而韩母则要他多注意身体，要吃好睡好。

在马车上，看着父母渐渐远去的身影，韩立咬紧了嘴唇，强忍着不让自己眼框中的泪珠流出来。

他虽然从小就比其他孩子成熟的多，但毕竟还是个十岁的小孩，第一次出远门让他的心里有点伤感和彷徨。他年幼的心里暗暗下定了决心，等挣到了大钱就马上赶回来，和父母再也不分开。

韩立从未想到，此次出去后钱财的多少对他已失去了意义，他竟然走上了一条与凡人不同的仙业大道，走出了自己的修仙之路。
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

        # 总结
        logger.info("\n" + "=" * 60)
        logger.info("🎉 集成测试完成!")


    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())