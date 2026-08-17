# chroma

ChromaDB + SiliconFlow Embedding 学习项目。

## Quick Start

```bash
# 1. 安装依赖（会以可编辑模式安装本项目，examples 可直接 from core import ...）
uv sync

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 SILICONFLOW_API_KEY
```

## 示例脚本

```bash
# 文档 CRUD 演示（add / get / upsert / delete）
uv run python examples/insert_demo.py

# 向量搜索 + 元数据过滤
uv run python examples/query_demo.py

# 从 chroma/data/documents/ 批量导入文档（放 .txt / .md，建议 UTF-8）
uv run python examples/ingest_demo.py
```

## Architecture

```
query → Embedding → Chroma Vector Search → results
```

## 文件说明

```
chroma/
├── pyproject.toml              # uv 项目配置 & 依赖管理
├── core/                       # 通用模块
│   ├── config.py               # 配置管理（API Key、模型、参数）
│   ├── embedding.py            # Embedding 抽象 + SiliconFlow 实现
│   ├── chroma_client.py        # ChromaDB 客户端封装（CRUD + Search）
│   ├── loader.py               # 文档加载（.txt / .md）
│   └── splitter.py             # 文本分块（固定大小 + 重叠）
├── examples/                   # 示例脚本
│   ├── insert_demo.py          # 演示：文档 CRUD
│   ├── query_demo.py           # 演示：向量搜索 + 元数据过滤
│   └── ingest_demo.py          # 演示：批量导入文档
└── data/
    ├── documents/              # 待导入的文档
    └── chroma_db/              # ChromaDB 持久化存储
```

## Configuration

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `embedding_model` | `BAAI/bge-large-zh-v1.5` | Embedding 模型 |
| `chunk_size` | `500` | 分块大小（字符） |
| `chunk_overlap` | `50` | 分块重叠（字符） |
