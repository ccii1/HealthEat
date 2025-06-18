# 健康食谱助手 - 您的智能私人营养师

## 项目概述

健康食谱助手是一个基于 Python 开发的个人饮食管理助手，它能够帮助用户记录日常饮食，提供营养建议，促进健康的饮食习惯。

## 主要功能

- 智能对话式饮食记录：支持自然语言输入饮食信息
- 多用户管理：支持多个用户独立使用
- 食物分类：自动对食物进行分类管理
- 营养建议：基于用户的饮食记录提供个性化的营养建议
- 自定义语气：支持轻松、幽默、正式三种回复风格

## 技术架构

- 前端界面：使用 Gradio 构建美观易用的 Web 界面
- 数据存储：使用 SQLite 数据库
- 智能对话：集成语言模型实现智能交互
- 日志系统：使用 loguru 实现分级日志管理

## 项目结构

```
├── agent/              # 智能代理模块
│   ├── workflow.py     # 工作流程处理
│   └── LlmChainGenerate.py  # 语言模型链生成
├── db/                 # 数据库模块
│   ├── SQLiteDB.py     # SQLite数据库操作
│   └── healthMealAssistant.db # 数据库文件
├── log/                # 日志模块
│   ├── logger.py       # 日志处理
│   └── log_config.json # 日志配置
├── utils/              # 工具模块
│   └── LLMUtil.py      # LLM工具
├── prompts/            # 提示词模板
│   ├── sql_generate.txt # SQL生成提示词
│   ├── judge_query.txt # 查询判断提示词
│   ├── conclude.txt    # 结论生成提示词
│   ├── judge_username.txt # 用户名判断提示词
│   └── sql_check.txt   # SQL检查提示词
└── app.py              # Web应用入口
```

## 安装依赖包

```bash
pip install -r requirements.txt
```

## 使用方法

### Web 界面启动

```bash
python app.py
```

启动后访问本地 Web 界面，支持以下功能：

- 用户注册和登录
- 选择语气风格（轻松/幽默/正式）
- 输入自然语言记录饮食
- 查询历史饮食记录和获取营养建议

## 示例用法

1. 记录饮食："今天早餐吃了燕麦粥和牛奶"
2. 查询记录："这周我吃了哪些食物"
3. 获取建议："我应该补充什么营养"

## 数据库结构

- users 表：存储用户信息
- food_categories 表：存储食物类别、营养价值和推荐食用频率
- meals 表：存储用户的饮食记录，包括日期、用餐类型和食物信息

#### 可能的小 bug

第一次使用请先在本地删除数据库文件，即 healthMealAssistant.db，第一次运行会自动创建该文件
