"""
演示：将文档插入 ChromaDB（使用 SiliconFlow Embedding）。

演示内容：add / get / upsert / delete 完整 CRUD 操作。

运行：
    uv run python examples/insert_demo.py
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

from core import ChromaClient, settings

COLLECTION = "demo"


class NoteMetadata(TypedDict):
    source: str
    category: str
    version: NotRequired[int]


sample_docs: list[str] = [
    "Redis 是一个开源的内存数据结构存储系统，可用作数据库、缓存和消息代理。",
    "Python 是一种解释型高级编程语言，以简洁可读的语法著称。",
]

sample_metadatas: list[NoteMetadata] = [
    {"source": "notes.md", "category": "database"},
    {"source": "notes.md", "category": "language"},
]

if __name__ == "__main__":
    # 持久化到本地目录（默认 chroma/data/chroma_db，可用 CHROMA_PERSIST_DIR 覆盖）
    client = ChromaClient()
    print(f"持久化目录: {settings.chroma_persist_dir}")

    # 重复运行时先清空同名 collection，避免 id 冲突
    if COLLECTION in client.list_collections():
        client.delete_collection(COLLECTION)
        print(f"已删除已有集合 '{COLLECTION}'")

    ids = [f"doc_{i}" for i in range(len(sample_docs))]

    client.add_documents(
        collection_name=COLLECTION,
        ids=ids,
        documents=sample_docs,
        metadatas=sample_metadatas,
    )
    print(f"已插入 {len(ids)} 条文档到集合 '{COLLECTION}'")

    result = client.get_documents(COLLECTION)
    print(f"集合当前共有 {len(result['ids'])} 条文档")
    print(result.get("documents"))

    upsert_meta: list[NoteMetadata] = [
        {"source": "notes.md", "category": "database", "version": 2}
    ]
    client.upsert_documents(
        collection_name=COLLECTION,
        ids=["doc_0"],
        documents=["Redis 支持多种数据结构：字符串、哈希、列表、集合、有序集合等。"],
        metadatas=upsert_meta,
    )
    print("已 upsert doc_0 的新内容")

    client.delete_documents(COLLECTION, ids=["doc_1"])
    result = client.get_documents(COLLECTION)
    print(f"删除 doc_1 后，集合共有 {len(result['ids'])} 条文档")
    print(result.get("documents"))
    print(f"\n数据已写入: {settings.chroma_persist_dir}")

