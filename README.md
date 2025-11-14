# mine-fanren

凡人修仙传数据挖掘项目

## 项目简介

本项目针对《凡人修仙传》小说进行数据挖掘和分析，通过文本处理和数据分析技术，提取小说中的人物、情节、修炼体系等信息。

## 数据来源

小说文本数据来源于：https://github.com/yuanxiaosc/fan-ren-xiu-xian-zhuan

由于文件较大（15MB），文本文件已移出版本控制。

**文件编码说明：** 小说文本文件 `1.txt` 使用 GB2312 编码格式，在读取时需要进行编码转换。

## 项目结构

```
mine-fanren/
├── README.md           # 项目说明文档
├── pyproject.toml      # Python项目配置
├── scripts/            # 运行脚本目录
│   ├── install_deps.py # 安装依赖脚本
│   ├── run_task_generator.py # 任务生成器脚本
│   └── README.md       # 脚本说明
├── src/                # 源代码目录
│   ├── models.py       # 数据模型
│   ├── store/          # 数据存储
│   ├── imod/           # 智能模块
│   └── workunit/       # 工作单元
├── resources/          # 资源文件目录
│   └── ignored/        # 不纳入git的文件目录
│       ├── 1.txt      # 小说文本数据
│       └── sqlite.db   # SQLite数据库
└── .venv/             # Python虚拟环境
```

## 快速开始

### 1. 安装依赖
```bash
python3 scripts/install_deps.py
```

### 2. 运行任务生成器
```bash
python3 scripts/run_task_generator.py
```

## 当前状态

- ✅ 完整的数据存储架构
- ✅ 智能抽取模块（实体关系、事实陈述）
- ✅ 任务生成和工作单元系统
- ✅ 文本切块和预处理功能

## 环境要求

- Python >= 3.12
- 依赖包：pydantic, langchain, python-dotenv

## 核心组件

### 工作单元 (src/workunit/)
- **FanrenTaskGeneratorWorkUnit** - 任务生成器
- **ERClaimWorkUnit** - 实体关系和事实抽取

### 智能模块 (src/imod/)
- **FanrenEntityExtractor** - 实体关系抽取
- **FanrenClaimExtractor** - 事实陈述抽取

### 数据存储 (src/store/)
- **SQLite数据库** - 章节块、任务、抽取结果存储
- **Repository模式** - 数据访问层