"""
集中配置管理。

配置项优先从环境变量（.env）读取，未设置时使用合理默认值。
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# 项目根目录（chroma/），不是 core/
BASE_DIR = Path(__file__).resolve().parent.parent


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return default if raw is None or raw == "" else int(raw)


class Settings(BaseModel):
    # SiliconFlow 配置
    siliconflow_api_key: str = os.getenv("SILICONFLOW_API_KEY", "")
    siliconflow_base_url: str = os.getenv(
        "SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"
    )
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")

    # ChromaDB 配置
    chroma_persist_dir: str = os.getenv(
        "CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db")
    )
    default_collection: str = os.getenv("DEFAULT_COLLECTION", "default")

    # 文档处理配置
    chunk_size: int = _env_int("CHUNK_SIZE", 500)
    chunk_overlap: int = _env_int("CHUNK_OVERLAP", 50)


settings = Settings()
