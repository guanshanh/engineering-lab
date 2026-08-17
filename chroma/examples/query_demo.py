"""
演示：向量搜索 + 元数据过滤。

演示内容：similarity_search、where 条件过滤。
说明：Chroma cosine 空间返回的是 distance（越小越相似）；
      相似度可近似为 similarity = 1 - distance（越大越相似）。

运行：
    uv run python examples/query_demo.py
"""

from __future__ import annotations

from typing import TypedDict

from chromadb.api.types import QueryResult

from core import ChromaClient, settings

COLLECTION = "demo"


class NoteMetadata(TypedDict):
    source: str
    category: str
    page: int


sample_docs: list[str] = [
    "Redis 是一个开源的内存数据结构存储系统，可用作数据库、缓存和消息代理。",
    "Memcached 是一个高性能的分布式内存对象缓存系统，常用于减轻数据库负载。",
    "MySQL 是一种关系型数据库管理系统，使用 SQL 进行数据查询与管理。",
    "PostgreSQL 是功能强大的开源对象关系型数据库，支持复杂查询与事务。",
    "MongoDB 是面向文档的 NoSQL 数据库，以 BSON 格式存储灵活的半结构化数据。",
    "Python 是一种解释型高级编程语言，以简洁可读的语法著称。",
    "JavaScript 是一种主要用于网页交互的脚本语言，也可在 Node.js 服务端运行。",
    "Docker 是一种容器化平台，可将应用及其依赖打包成可移植的镜像。",
    "Kubernetes 是容器编排系统，用于自动化部署、扩缩容和管理容器化应用。",
    "HTTP 是超文本传输协议，定义了浏览器与服务器之间交换资源的请求与响应格式。",
]

sample_metadatas: list[NoteMetadata] = [
    {"source": "notes.md", "category": "database", "page": 1},
    {"source": "notes.md", "category": "database", "page": 2},
    {"source": "notes.md", "category": "database", "page": 3},
    {"source": "notes.md", "category": "database", "page": 4},
    {"source": "notes.md", "category": "database", "page": 5},
    {"source": "notes.md", "category": "language", "page": 6},
    {"source": "notes.md", "category": "language", "page": 7},
    {"source": "notes.md", "category": "infra", "page": 8},
    {"source": "notes.md", "category": "infra", "page": 9},
    {"source": "notes.md", "category": "network", "page": 10},
]


def print_hits(results: QueryResult, *, limit: int | None = None) -> None:
    """打印 distance（越小越好）与 similarity=1-distance（越大越好）。"""
    documents = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if results["distances"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    rows = list(zip(documents, distances, metadatas))
    if limit is not None:
        rows = rows[:limit]
    for rank, (doc, dist, meta) in enumerate(rows, start=1):
        similarity = 1.0 - float(dist)
        category = meta.get("category", "?") if meta else "?"
        print(
            f"  #{rank} similarity={similarity:.4f}  distance={float(dist):.4f}"
            f"  [{category}] {doc}"
        )


if __name__ == "__main__":
    client = ChromaClient()
    print(f"持久化目录: {settings.chroma_persist_dir}")

    if COLLECTION in client.list_collections():
        client.delete_collection(COLLECTION)

    ids = [f"doc_{i}" for i in range(len(sample_docs))]
    client.add_documents(COLLECTION, ids, sample_docs, sample_metadatas)
    print(f"已插入 {len(ids)} 条文档\n")

    print("=== 相似度搜索: '什么是缓存数据库'（top 5）===")
    print("（similarity 越大越像；distance 越小越像）")
    results = client.similarity_search(COLLECTION, "什么是缓存数据库", n_results=5)
    print_hits(results)

    print("\n=== 相似度搜索: '容器怎么编排部署'（top 5）===")
    results = client.similarity_search(COLLECTION, "容器怎么编排部署", n_results=5)
    print_hits(results)

    print("\n=== 过滤: category='database' ===")
    results = client.similarity_search(
        COLLECTION,
        "数据库",
        n_results=5,
        where={"category": "database"},
    )
    print_hits(results)

    print("\n=== 过滤: category='language' ===")
    results = client.similarity_search(
        COLLECTION,
        "编程语言",
        n_results=5,
        where={"category": "language"},
    )
    print_hits(results)
