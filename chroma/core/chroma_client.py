"""
ChromaDB 客户端封装。

提供统一接口，支持 ChromaDB 的内存模式和持久化模式，
包含 Collection 管理和文档 CRUD 操作。

核心概念：
    - Client：数据库连接（内存模式或持久化模式）
    - Collection：类似"表"——存储文档 + 向量 + 元数据
    - 文档 CRUD：add / get / update / delete / upsert

类型边界：
    - SiliconFlow Embedding 返回 list[float] / list[list[float]]
    - 写入 / 查询 Chroma 前转换为 Embeddings（float32 ndarray）
"""

from __future__ import annotations

import chromadb
from chromadb import Collection
from chromadb.api.types import GetResult, QueryResult

from .config import settings
from .embedding import SiliconFlowEmbedding
from .types import DocMetadatas, Where, to_embedding, to_embeddings, to_metadatas


class ChromaClient:
    def __init__(
        self,
        persist_dir: str | None = None,
        in_memory: bool = False,
    ) -> None:
        if in_memory:
            # 内存模式：数据仅存于内存，进程退出后丢失，适合测试
            self._client = chromadb.Client()
        else:
            # 持久化模式：数据写入本地磁盘目录，重启后仍可用
            path = persist_dir or settings.chroma_persist_dir
            self._client = chromadb.PersistentClient(path=path)

        # 用于将文本转换为向量的 embedding 模型客户端
        self._embedding = SiliconFlowEmbedding()

    # ── Collection 管理 ──────────────────────────────────────────────

    def create_collection(self, name: str) -> Collection:
        # get_or_create_collection: 若 collection 已存在则获取，否则新建
        # metadata 中 hnsw:space=cosine 表示使用余弦相似度作为向量距离度量
        return self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def get_collection(self, name: str) -> Collection:
        # 获取已存在的 collection，不存在则抛出异常
        return self._client.get_collection(name=name)

    def delete_collection(self, name: str) -> None:
        # 删除整个 collection 及其所有数据（不可恢复）
        self._client.delete_collection(name=name)

    def list_collections(self) -> list[str]:
        # 列出当前数据库中所有 collection 的名称
        return [c.name for c in self._client.list_collections()]

    # ── 文档 CRUD ────────────────────────────────────────────────────

    def add_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        metadatas: DocMetadatas | None = None,
    ) -> None:
        """通过 SiliconFlow 生成向量并插入 Chroma。"""
        col = self.create_collection(collection_name)
        embeddings = to_embeddings(self._embedding.embed_batch(documents))
        col.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=to_metadatas(metadatas),
        )

    def get_documents(
        self,
        collection_name: str,
        ids: list[str] | None = None,
        where: Where | None = None,
        limit: int | None = None,
    ) -> GetResult:
        """按 id 或元数据条件获取文档（非向量搜索，精确查询）。"""
        col = self.get_collection(collection_name)
        return col.get(ids=ids, where=where, limit=limit)

    def update_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str] | None = None,
        metadatas: DocMetadatas | None = None,
    ) -> None:
        """更新已有文档的内容或元数据，id 不存在则忽略。"""
        col = self.get_collection(collection_name)
        embeddings = (
            to_embeddings(self._embedding.embed_batch(documents))
            if documents is not None
            else None
        )
        col.update(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=to_metadatas(metadatas),
        )

    def delete_documents(
        self,
        collection_name: str,
        ids: list[str] | None = None,
        where: Where | None = None,
    ) -> None:
        """删除文档，可按 id 列表或元数据条件删除。"""
        col = self.get_collection(collection_name)
        col.delete(ids=ids, where=where)

    def upsert_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        metadatas: DocMetadatas | None = None,
    ) -> None:
        """upsert = insert + update：id 不存在则插入，已存在则覆盖。"""
        col = self.create_collection(collection_name)
        embeddings = to_embeddings(self._embedding.embed_batch(documents))
        col.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=to_metadatas(metadatas),
        )

    # ── 向量搜索 ────────────────────────────────────────────────────

    def similarity_search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Where | None = None,
    ) -> QueryResult:
        """
        将查询文本转换为向量，然后在 Chroma 中搜索最近邻。

        返回包含 ids, documents, distances, metadatas 的 QueryResult。
        """
        col = self.get_collection(collection_name)
        query_embedding = to_embedding(self._embedding.embed_text(query))
        # print(query_embedding)
        return col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
