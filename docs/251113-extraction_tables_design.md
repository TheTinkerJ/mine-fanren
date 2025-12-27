# 实体关系提取结果存储表设计

**日期**: 2025-11-13
**版本**: 1.0

## 概述

为 er_claim 任务的提取结果设计三张核心存储表，用于存储LLM从文本中提取的实体、关系和事实陈述。每条抽取记录使用自增ID，保持简洁性。

## 背景

- 项目需要处理2000+章节块的文本提取
- er_claim 任务同时提取实体关系和事实陈述
- 提取结果需要持久化存储以支持后续查询和分析
- 避免复杂的UUID维护，采用简单直接的设计

## 表结构设计

### 1. entity_extractions (实体抽取记录表)

存储每次实体抽取的结果记录，一条记录对应一个实体在特定章节块中的出现。

```sql
CREATE TABLE IF NOT EXISTS entity_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    chunk_id TEXT NOT NULL,                          -- 关联章节块ID
    task_id TEXT NOT NULL,                           -- 关联抽取任务ID

    -- 抽取结果字段
    entity_name TEXT NOT NULL,                       -- 实体名称 (如"韩立", "掌天瓶")
    entity_category TEXT NOT NULL,                   -- 实体类别 (如"人物", "物品", "地点")
    entity_description TEXT,                         -- 实体描述 (LLM提取的描述信息)

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间

    -- 外键约束
    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
);
```

**字段说明**:
- `extraction_id`: 每条抽取记录的唯一标识，使用自增ID
- `entity_name`: 从文本中提取的原始实体名称
- `entity_category`: 实体分类，如人物、地点、物品、功法、组织等
- `entity_description`: LLM对实体的描述信息

### 2. relation_extractions (关系抽取记录表)

存储每次关系抽取的结果记录，一条记录对应两个实体之间的关系。

```sql
CREATE TABLE IF NOT EXISTS relation_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    chunk_id TEXT NOT NULL,                          -- 关联章节块ID
    task_id TEXT NOT NULL,                           -- 关联抽取任务ID

    -- 抽取结果字段
    source_entity TEXT NOT NULL,                     -- 关系源实体
    target_entity TEXT NOT NULL,                     -- 关系目标实体
    relationship_type TEXT,                          -- 关系类型 (如"师徒", "敌对", "拥有")
    relationship_description TEXT,                   -- 关系描述 (LLM提取的描述信息)

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间

    -- 外键约束
    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
);
```

**字段说明**:
- `source_entity`: 关系的发起方实体
- `target_entity`: 关系的接收方实体
- `relationship_type`: 关系分类，可能包括师徒、敌对、拥有、隶属、亲属等
- `relationship_description`: LLM对关系的详细描述

### 3. claim_extractions (事实陈述抽取记录表)

存储每次事实陈述抽取的结果记录，一条记录对应一个事实陈述。

```sql
CREATE TABLE IF NOT EXISTS claim_extractions (
    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    chunk_id TEXT NOT NULL,                          -- 关联章节块ID
    task_id TEXT NOT NULL,                           -- 关联抽取任务ID

    -- 抽取结果字段
    claim_category TEXT NOT NULL,                    -- 事实类别 (如"战斗", "修炼", "情节发展")
    claim_subject TEXT NOT NULL,                     -- 事实主体
    claim_content TEXT NOT NULL,                     -- 事实内容描述

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间

    -- 外键约束
    FOREIGN KEY (chunk_id) REFERENCES chapter_chunks(chunk_id),
    FOREIGN KEY (task_id) REFERENCES chapter_chunk_task(task_id)
);
```

**字段说明**:
- `claim_category`: 事实陈述的分类，如战斗、修炼、情节发展、对话、情感变化等
- `claim_subject`: 事实的主要参与者或对象
- `claim_content`: 具体的事实内容描述

## 索引设计

为优化查询性能，设计以下索引：

### entity_extractions 索引
```sql
CREATE INDEX IF NOT EXISTS idx_entity_chunk ON entity_extractions(chunk_id);
CREATE INDEX IF NOT EXISTS idx_entity_task ON entity_extractions(task_id);
CREATE INDEX IF NOT EXISTS idx_entity_name ON entity_extractions(entity_name);
CREATE INDEX IF NOT EXISTS idx_entity_category ON entity_extractions(entity_category);
CREATE INDEX IF NOT EXISTS idx_entity_created_at ON entity_extractions(created_at);
```

### relation_extractions 索引
```sql
CREATE INDEX IF NOT EXISTS idx_relation_chunk ON relation_extractions(chunk_id);
CREATE INDEX IF NOT EXISTS idx_relation_task ON relation_extractions(task_id);
CREATE INDEX IF NOT EXISTS idx_relation_source ON relation_extractions(source_entity);
CREATE INDEX IF NOT EXISTS idx_relation_target ON relation_extractions(target_entity);
CREATE INDEX IF NOT EXISTS idx_relation_type ON relation_extractions(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relation_created_at ON relation_extractions(created_at);
```

### claim_extractions 索引
```sql
CREATE INDEX IF NOT EXISTS idx_claim_chunk ON claim_extractions(chunk_id);
CREATE INDEX IF NOT EXISTS idx_claim_task ON claim_extractions(task_id);
CREATE INDEX IF NOT EXISTS idx_claim_category ON claim_extractions(claim_category);
CREATE INDEX IF NOT EXISTS idx_claim_subject ON claim_extractions(claim_subject);
CREATE INDEX IF NOT EXISTS idx_claim_created_at ON claim_extractions(created_at);
```

## 设计原则

### 1. 简洁性原则
- 使用自增ID作为主键，避免UUID的复杂性和存储开销
- 每条抽取记录独立存储，不需要复杂的规范化处理
- 表结构简单明了，便于理解和维护

### 2. 可追溯性原则
- 所有记录都关联 `chunk_id` 和 `task_id`，支持完整的抽取链路追踪
- 时间戳记录抽取时间，便于调试和分析
- 保留原始提取结果，支持后续的重新处理

### 3. 查询友好原则
- 按章节块查询：获取某个章节块的所有实体、关系、事实
- 按任务查询：获取某个任务的抽取结果
- 按内容搜索：按实体名称、关系类型、事实类别搜索
- 统计分析：各类抽取结果的数量和分布

### 4. 扩展性原则
- 表结构简单，后续可根据需要添加新字段
- 独立表设计，便于后续引入实体规范化
- 不预设复杂的关联关系，保持灵活性

## 预期查询场景

### 1. 按章节块查询
```sql
-- 查询某个章节块的所有实体
SELECT * FROM entity_extractions WHERE chunk_id = ?;

-- 查询某个章节块的所有关系
SELECT * FROM relation_extractions WHERE chunk_id = ?;

-- 查询某个章节块的所有事实陈述
SELECT * FROM claim_extractions WHERE chunk_id = ?;
```

### 2. 按任务查询
```sql
-- 查询某个任务的抽取结果
SELECT * FROM entity_extractions WHERE task_id = ?;
SELECT * FROM relation_extractions WHERE task_id = ?;
SELECT * FROM claim_extractions WHERE task_id = ?;
```

### 3. 内容搜索
```sql
-- 按实体名称搜索
SELECT * FROM entity_extractions WHERE entity_name = '韩立';

-- 按关系类型搜索
SELECT * FROM relation_extractions WHERE relationship_type = '师徒';

-- 按事实类别搜索
SELECT * FROM claim_extractions WHERE claim_category = '修炼';
```

### 4. 统计分析
```sql
-- 统计实体类别分布
SELECT entity_category, COUNT(*) FROM entity_extractions GROUP BY entity_category;

-- 统计关系类型分布
SELECT relationship_type, COUNT(*) FROM relation_extractions GROUP BY relationship_type;

-- 统计每章节的抽取量
SELECT chunk_id,
       (SELECT COUNT(*) FROM entity_extractions WHERE chunk_id = cc.chunk_id) as entity_count,
       (SELECT COUNT(*) FROM relation_extractions WHERE chunk_id = cc.chunk_id) as relation_count,
       (SELECT COUNT(*) FROM claim_extractions WHERE chunk_id = cc.chunk_id) as claim_count
FROM chapter_chunks cc;
```

## 实现计划

1. **✅ 设计文档**: 创建本设计文档
2. **DDL实现**: 在 `sqlite_ddl.py` 中添加表创建语句
3. **数据库初始化**: 更新 `init_database()` 函数
4. **数据模型**: 在 `models.py` 中添加对应的数据模型类
5. **数据访问层**: 在 `sqlite_repo.py` 中添加对应的Repo类
6. **测试验证**: 创建测试数据验证表结构

## 后续扩展方向

### 1. 实体规范化
当需要跨章节的实体分析时，可以引入：
- 规范化实体表 (`canonical_entities`)
- 实体别名映射表 (`entity_aliases`)
- 在抽取记录表中添加规范化实体ID

### 2. 置信度评分
为每条抽取记录添加置信度字段：
- 添加 `confidence_score` 字段
- 支持基于置信度的筛选和分析

### 3. 上下文信息
为抽取结果添加更多上下文：
- 添加 `context_snippet` 字段存储原文片段
- 添加 `position_info` 字段存储位置信息

### 4. 结果验证
支持人工验证和修正：
- 添加 `verified` 字段标记验证状态
- 添加 `verified_by` 字段记录验证人员
- 添加 `verified_at` 字段记录验证时间

## 总结

本设计采用简洁实用的方案，通过三张独立的抽取记录表存储实体、关系和事实陈述的提取结果。使用自增ID作为主键，避免复杂UUID维护，同时保持良好的查询性能和扩展性。该设计能够满足当前er_claim任务的存储需求，同时为未来的功能扩展预留了空间。