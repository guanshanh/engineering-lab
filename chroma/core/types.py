"""
共享类型与 Chroma 边界适配。

分层约定：
    - Embedding / HTTP 层：使用纯 Python 类型（list[float]）
    - 业务结构：用 TypedDict 描述已知字段
    - Chroma 写入边界：开放元数据用 Mapping；向量转为 Embeddings
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import NotRequired, TypedDict, cast

import numpy as np
from chromadb.api.types import Embedding, Embeddings, Metadata, Metadatas, Where

# Chroma 可索引的标量；写入侧元数据字段名开放时使用
MetaValue = str | int | float | bool
DocMetadatas = Sequence[Mapping[str, MetaValue]]


class SourceMetadata(TypedDict):
    """loader 产生的文件级元数据。"""

    source: str
    filename: str
    extension: str


class ChunkMetadata(TypedDict):
    """splitter 产生的分块元数据；可继承文件级字段。"""

    chunk_index: int
    char_start: int
    char_end: int
    source: NotRequired[str]
    filename: NotRequired[str]
    extension: NotRequired[str]


class DocumentRecord(TypedDict):
    """loader 返回的原始文档。"""

    text: str
    metadata: SourceMetadata


class ChunkRecord(TypedDict):
    """splitter 返回的分块。"""

    text: str
    metadata: ChunkMetadata


def to_metadatas(metadatas: DocMetadatas | None) -> Metadatas | None:
    """业务侧 metadata → chromadb Metadatas。"""
    if metadatas is None:
        return None
    return cast(Metadatas, list(metadatas))


def to_embedding(vector: list[float]) -> Embedding:
    """list[float] → chromadb Embedding（float32 ndarray）。"""
    return np.asarray(vector, dtype=np.float32)


def to_embeddings(vectors: list[list[float]]) -> Embeddings:
    """list[list[float]] → chromadb Embeddings。"""
    return [to_embedding(v) for v in vectors]


__all__ = [
    "MetaValue",
    "DocMetadatas",
    "SourceMetadata",
    "ChunkMetadata",
    "DocumentRecord",
    "ChunkRecord",
    "Embedding",
    "Embeddings",
    "Metadata",
    "Metadatas",
    "Where",
    "to_embedding",
    "to_embeddings",
    "to_metadatas",
]
