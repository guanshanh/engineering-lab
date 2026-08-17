# AGENTS.md

本仓库给 Cursor Agent / 协作者的约定。后续可按语言或子项目继续追加条目。

## Python

### 显式类型标注（要求）

编写或修改 Python 代码时，应使用**显式类型标注**，不要依赖推断省略公开接口的类型。

- 函数参数、返回值应标注类型
- 结构已知的数据不要长期用裸 `dict` / `list[dict]`；应定义成结构体（`TypedDict`、`dataclass`、`NamedTuple` 等），再在标注里引用
- 与第三方库交互时，优先使用库提供的类型，或在边界处做明确转换
- 仅当结构真正动态、字段不可预知时，才使用 `dict[str, ...]`

示例：

```python
from typing import TypedDict


class Item(TypedDict):
    id: str
    score: int


# 好：结构清晰，可读性和类型都更好
def process_items(name: str, items: list[Item]) -> list[str]: ...

items: list[Item] = [
    {"id": "1", "score": 10},
]

# 避免：结构已知却仍用裸 dict，类型含糊、可读性差
def process_items(name, items): ...
items = [{"id": "1", "score": 10}]
```

### 导入约定

- **包内模块**（如 `core/` 内部）：使用相对导入，例如 `from .config import settings`
- **包外代码**（如 `examples/`）：使用包绝对导入，例如 `from core import ChromaClient`、`from core.types import ChunkMetadata`
- 不要用 `sys.path.insert` 拼接项目路径来导入本地包；将包声明为可安装项目（`pyproject.toml` + `uv sync`）
