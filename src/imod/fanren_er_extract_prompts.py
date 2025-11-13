# 凡人实体提取 SystemMessage
from src.models import PromptTemplate


FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE = PromptTemplate.create_template(
    template_key="FANREN_ENTITY_EXTRACTION_SYSTEM_TEMPLATE",
    version="1.0.0",
    description="凡人小说实体提取系统提示词 - 基于fast_graphrag设计模式",
    template_content="""# DOMAIN
修仙小说知识图谱构建 - 从《凡人修仙传》等修仙小说文本中提取核心实体及其关系，构建完整的修仙世界观知识图谱。

# GOAL
你的目标是从给定的修仙小说文本中，提取所有对理解故事发展、人物关系和世界观构建有价值的核心实体，并识别它们之间的关系。重点关注实体在剧情中的持久性和关联性。

# 可能的查询示例:
- "韩立在七玄门时遇到了谁？"
- "韩立修炼的第一个功法是什么？"
- "掌天瓶有什么特殊功能？"
- "韩立在黄枫谷的地位如何？"
- "墨大夫和韩立的关系是什么？"

# INSTRUCTIONS
1. **实体识别**: 精确识别并提取所有属于规定实体类型的重要实体。为每个实体提供简洁的描述，捕捉其在修仙世界观中的关键特征和剧情重要性。使用标准化的实体名称，确保一致性。

2. **关系发现**: 识别并描述所有已提取实体之间的关系。解决代词指代问题，确保关系描述清晰说明实体间的连接。关系应反映修仙小说特有的逻辑（如师徒、敌对、宗门归属、法宝归属等）。

3. **实体覆盖检查**: 验证每个识别的实体都至少参与一个关系。如果存在孤立实体，推断并添加关系将其连接到图谱中，即使关系是隐含的。

4. **输出格式: 严格有效的JSON**: 输出必须是严格有效的JSON格式。遵循所有标准JSON规则。JSON必须包含两个顶级列表："entities" 和 "relationships"。每个列表项必须是具有必需字段的JSON对象（实体需要"name", "category", "desc"字段；关系需要"source", "target", "desc"字段），所有字段都必须是用双引号包围的JSON字符串。**绝对不允许使用单引号、方括号包围字符串、尾随逗号或markdown格式（如三个反引号）。** 无效的JSON输出是不可接受的。

# 7类核心实体类型说明
- **character**: 角色实体（主角、配角、反派、导师等有名字的角色）
- **state**: 状态实体（境界状态、位置状态、身份状态、健康状态等）
- **ability**: 能力实体（功法秘籍、法术神通、战斗技能、辅助技能等）
- **item**: 物品实体（法宝武器、丹药灵药、材料资源、符篆阵图等）
- **creature**: 生物实体（灵兽、妖兽、灵植、奇异生物、魔物等）
- **organization**: 组织实体（宗门势力、家族势力、商会组织、邪道势力等）
- **location**: 地点实体（城镇区域、修仙福地、危险区域、宗门驻地等）

# 示例输入数据
文档: "韩立在七玄门中遇到了自己的第一个师傅墨大夫，墨大夫传授了他长春功，帮助他踏上了修仙之路。后来韩立加入了黄枫谷，在那里他修炼了青元剑诀，并获得了掌天瓶这个神秘的法宝。"

# 示例输出数据 (有效JSON - 不得偏离)
{{
  "entities": [
    {{"name": "韩立", "category": "character", "desc": "修仙小说的主角，资质平凡但意志坚定"}},
    {{"name": "墨大夫", "category": "character", "desc": "韩立的第一个师傅，传授长春功的引路人"}},
    {{"name": "七玄门", "category": "organization", "desc": "韩立最初接触的世俗武学门派"}},
    {{"name": "长春功", "category": "ability", "desc": "韩立修炼的第一部功法，基础修仙法门"}},
    {{"name": "黄枫谷", "category": "organization", "desc": "韩立加入的修仙宗门，正道门派之一"}},
    {{"name": "青元剑诀", "category": "ability", "desc": "韩立在黄枫谷修炼的主要剑法功法"}},
    {{"name": "掌天瓶", "category": "item", "desc": "韩立获得的神秘法宝，具有特殊时空能力"}},
    {{"name": "修仙之路", "category": "state", "desc": "韩立踏上修仙道路的状态转变"}}
  ],
  "relationships": [
    {{"source": "韩立", "target": "墨大夫", "desc": "墨大夫是韩立的第一个修仙师傅"}},
    {{"source": "韩立", "target": "七玄门", "desc": "韩立曾是七玄门的弟子"}},
    {{"source": "墨大夫", "target": "长春功", "desc": "墨大夫将长春功传授给韩立"}},
    {{"source": "韩立", "target": "长春功", "desc": "韩立通过长春功踏上修仙之路"}},
    {{"source": "韩立", "target": "黄枫谷", "desc": "韩立加入黄枫谷成为修仙弟子"}},
    {{"source": "韩立", "target": "青元剑诀", "desc": "韩立在黄枫谷修炼青元剑诀"}},
    {{"source": "韩立", "target": "掌天瓶", "desc": "韩立获得了掌天瓶这个神秘法宝"}}
  ]
}}""",
    required_params=[],  # 系统模板没有变量，只需要输入文本
    language="zh",
    notes="基于JSON格式的实体提取系统提示词"
)


# 凡人实体提取 UserMessage
FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE = PromptTemplate.create_template(
    template_key="FANREN_ENTITY_EXTRACTION_PROMPT_TEMPLATE",
    version="1.0.0",
    description="凡人小说实体提取用户提示词",
    template_content="""**重要的JSON格式规则:**
- **按照示例输出包含所有识别实体和关系的严格有效JSON。**
- **不要使用方括号或单引号 `(}},],')` 来包围JSON中的字符串。**
- **确保列表或对象中没有尾随逗号。**
- **输出必须是单个有效的JSON对象。不要用三个反引号或任何其他markdown格式包装JSON输出。**

# 输入数据
<<DOCUMENT_START>>
**文档**:
{input_text}
<<DOCUMENT_END>>

输出:""",
    required_params=["input_text"],
    language="zh",
    notes="用户提示词模板，用于实体提取请求，强调JSON格式要求"
)