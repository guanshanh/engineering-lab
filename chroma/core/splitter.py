"""
文本分块器 —— 将长文本切分为带重叠的固定大小块，用于 Embedding。

为什么要分块？
    LLM 上下文窗口和 Embedding 模型都有 token 限制。
    较小的块也能提高检索精度：一个 500 字符的关于"Redis 持久化"的块，
    比一个仅提及一次的 10000 字符文档，在该查询上得分更高。

重叠（Overlap）确保块边界处的句子不会丢失。
每个块携带自己的元数据（索引、字符偏移、来源）。
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from .config import settings
from .types import ChunkMetadata, ChunkRecord, MetaValue


def split_chunks(
    text: str,
    metadata: Mapping[str, MetaValue] | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[ChunkRecord]:
    """
    将文本按固定大小切分为带重叠的块。

    返回列表：
        {"text": "...", "metadata": {"chunk_index": 0, "char_start": 0, ...}}
    """
    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap
    base_meta = dict(metadata or {})

    chunks: list[ChunkRecord] = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + size
        chunk_text = text[start:end]

        chunk_meta = cast(
            ChunkMetadata,
            {
                **base_meta,
                "chunk_index": idx,
                "char_start": start,
                "char_end": min(end, len(text)),
            },
        )
        chunks.append({"text": chunk_text, "metadata": chunk_meta})

        start += size - overlap
        idx += 1

    print(chunks)
    print(len(chunks))
    return chunks
