"""
文档加载器 —— 读取 .txt 和 .md 文件并转换为标准格式。

返回 DocumentRecord：
    - text：文件完整内容
    - metadata：文件路径、文件名、扩展名（Chroma 可索引标量）
"""

from __future__ import annotations

from pathlib import Path

from .types import DocumentRecord

# Windows 记事本等常见：UTF-8 / 带 BOM / 系统中文编码
_TEXT_ENCODINGS: tuple[str, ...] = ("utf-8-sig", "utf-8", "gb18030")


def _read_text(path: Path) -> str:
    """按多种编码尝试读取文本，避免中文 Windows 下 GBK 文件报错。"""
    raw = path.read_bytes()
    errors: list[str] = []
    for encoding in _TEXT_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError(
        f"无法解码文件 {path}，已尝试 {_TEXT_ENCODINGS}。\n" + "\n".join(errors)
    )


def load_document(file_path: str | Path) -> DocumentRecord:
    path = Path(file_path)
    if path.suffix.lower() not in (".txt", ".md"):
        raise ValueError(f"不支持的文件类型: {path.suffix}")

    text = _read_text(path)
    return {
        "text": text,
        "metadata": {
            "source": str(path),
            "filename": path.name,
            "extension": path.suffix.lower(),
        },
    }


def load_directory(dir_path: str | Path) -> list[DocumentRecord]:
    """加载目录下所有支持的文件。"""
    directory = Path(dir_path)
    docs: list[DocumentRecord] = []
    for ext in ("*.txt", "*.md"):
        for f in sorted(directory.glob(ext)):
            docs.append(load_document(f))
    return docs
