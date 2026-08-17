"""
SiliconFlow Embedding 客户端。

调用 SiliconFlow /v1/embeddings API 将文本转换为稠密向量。
支持单条文本和批量文本的 Embedding。

本模块保持 API 原生返回类型：
    embed_text  -> list[float]
    embed_batch -> list[list[float]]

写入 Chroma 前请在边界层转换为 chromadb.Embeddings（见 core.types.to_embeddings）。

用法：
    from core import SiliconFlowEmbedding
    emb = SiliconFlowEmbedding()
    vectors = emb.embed_batch(["hello", "world"])
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import requests

from .config import settings


# ── 抽象基类 ─────────────────────────────────────────────────────────
# 后续接入 OpenAI / 本地模型时，只需实现此接口即可。

class BaseEmbedding(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        ...


# ── SiliconFlow 实现 ─────────────────────────────────────────────────

class SiliconFlowEmbedding(BaseEmbedding):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.siliconflow_api_key
        self.model = model or settings.embedding_model
        self.base_url = base_url or settings.siliconflow_base_url
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY 未设置")

    def _call_api(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": texts}

        # print(f"[embedding] 请求 SiliconFlow: model={self.model}, texts={len(texts)}")
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # API 返回的 embedding 按 index 排序
        sorted_items = sorted(data["data"], key=lambda x: x["index"])
        embeddings = [item["embedding"] for item in sorted_items]
        dim = len(embeddings[0]) if embeddings else 0
        print(f"[embedding] 完成: count={len(embeddings)}, dim={dim}")
        return embeddings

    # ── 公开接口 ─────────────────────────────────────────────────────

    def embed_text(self, text: str) -> list[float]:
        return self._call_api([text])[0]

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """分批将文本列表转换为向量，避免超出 API 限制。"""
        all_embeddings: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            all_embeddings.extend(self._call_api(chunk))
        return all_embeddings
