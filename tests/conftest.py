"""
pytest 全局配置文件。

说明：
- 本项目采用 src/ 目录布局（源码在 src/code_packager）。
- 在使用 `pdm run pytest` 时，通常会以 editable 方式安装项目，因此可以直接 import code_packager。
- 但为了让测试在“未安装项目、直接从仓库跑 pytest”的情况下也能工作，这里将 src 目录加入 sys.path。
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_syspath() -> None:
    """
    确保 src 目录在 sys.path 中。

    这样 `import code_packager` 会从 src/code_packager 解析到源码。
    """

    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"

    # 只有在 src 真实存在且不在 sys.path 时才插入，避免影响其它环境。
    if src_dir.exists() and src_dir.is_dir():
        src_str = str(src_dir)
        if src_str not in sys.path:
            sys.path.insert(0, src_str)


_ensure_src_on_syspath()

