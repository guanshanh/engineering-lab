"""
演示：从 data/documents/ 目录导入文档到 ChromaDB。

流程：读取文件 → 分块 → Embedding → 写入 Chroma

运行：
    uv run python examples/ingest_demo.py
"""

from __future__ import annotations

import hashlib
import sys

from core import ChromaClient, load_directory, settings, split_chunks
from core.config import BASE_DIR
from core.types import ChunkMetadata

# 与 README 一致：chroma/data/documents/（不是 examples/data/...）
DOC_DIR = BASE_DIR / "data" / "documents"


def make_chunk_id(text: str, source: str, index: int) -> str:
    """生成确定性 ID，使重复导入同一文件时具有幂等性。"""
    content = f"{source}::{index}::{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


if __name__ == "__main__":
    doc_dir = DOC_DIR
    supported = (
        list(doc_dir.glob("*.txt")) + list(doc_dir.glob("*.md"))
        if doc_dir.is_dir()
        else []
    )
    if not supported:
        print(f"未在 {doc_dir} 中找到 .txt / .md 文件")
        print("请把文档放到 chroma/data/documents/ 后重新运行。")
        sys.exit(1)

    docs = load_directory(doc_dir)
    print(f"已加载 {len(docs)} 个文件")

    client = ChromaClient()
    total = 0

    for doc in docs:
        chunks = split_chunks(doc["text"], doc["metadata"])
        ids = [
            make_chunk_id(
                c["text"],
                str(doc["metadata"]["source"]),
                c["metadata"]["chunk_index"],
            )
            for c in chunks
        ]
        texts = [c["text"] for c in chunks]
        metas: list[ChunkMetadata] = [c["metadata"] for c in chunks]

        client.add_documents(
            collection_name=settings.default_collection,
            ids=ids,
            documents=texts,
            metadatas=metas,
        )
        total += len(chunks)
        print(f"  {doc['metadata']['filename']}: {len(chunks)} 个块")

    print(f"\n共导入 {total} 个块到集合 '{settings.default_collection}'")
