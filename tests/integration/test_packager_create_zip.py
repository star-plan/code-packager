"""
CodePackager.create_zip() 的集成测试。

特点：
- 使用 tmp_path 构造一个真实的文件树
- 调用 create_zip() 生成真实 zip 文件
- 校验 zip 内文件集合、统计信息、以及“去除注释”选项是否生效
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from pathspec import PathSpec

from code_packager.packager import CodePackager


def _zip_names(zip_path: Path) -> set[str]:
    """
    读取 zip 内文件名集合，并做分隔符归一化（避免 Windows \\ 与 zip / 的差异）。
    """

    with zipfile.ZipFile(zip_path, "r") as zf:
        return {name.replace("\\", "/") for name in zf.namelist()}


def test_create_zip_respects_global_and_gitignore_rules(tmp_path: Path) -> None:
    """
    - 全局规则：排除 *.log
    - 根目录 .gitignore：排除 node_modules/
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()

    # 根目录文件
    (source_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (source_dir / "debug.log").write_text("should be excluded\n", encoding="utf-8")

    # node_modules 目录（应被 .gitignore 排除）
    node_modules = source_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "lib.js").write_text("console.log(1)\n", encoding="utf-8")

    # 根目录 .gitignore
    (source_dir / ".gitignore").write_text("node_modules/\n", encoding="utf-8")

    output_zip = tmp_path / "out.zip"

    global_spec = PathSpec.from_lines("gitwildmatch", ["*.log"])
    packager = CodePackager(global_spec)
    stats = packager.create_zip(str(source_dir), str(output_zip), remove_comments=False, compression_method="deflate")

    assert output_zip.exists()
    assert stats["total_files"] >= 2
    assert stats["included_files"] >= 1
    assert stats["excluded_files"] >= 1
    assert stats["compressed_size"] > 0

    names = _zip_names(output_zip)
    assert "main.py" in names
    assert "debug.log" not in names
    assert "node_modules/lib.js" not in names


def test_create_zip_remove_comments_modifies_python_files(tmp_path: Path) -> None:
    """
    remove_comments=True 时，.py 文件写入 zip 的内容应为“去注释/去 docstring 后”的结果。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()

    (source_dir / ".gitignore").write_text("", encoding="utf-8")

    py_file = source_dir / "sample.py"
    py_file.write_text(
        '''"""module docstring should be removed"""

def f():
    """function docstring should be removed"""
    x = 1  # inline comment should be removed
    s = "# hash inside string should stay"
    return x, s
''',
        encoding="utf-8",
    )

    output_zip = tmp_path / "out.zip"
    global_spec = PathSpec.from_lines("gitwildmatch", [])
    packager = CodePackager(global_spec)
    stats = packager.create_zip(str(source_dir), str(output_zip), remove_comments=True, compression_method="deflate")

    assert output_zip.exists()
    assert stats["files_with_comments_removed"] >= 1

    with zipfile.ZipFile(output_zip, "r") as zf:
        content = zf.read("sample.py").decode("utf-8", errors="replace")

    assert "module docstring should be removed" not in content
    assert "function docstring should be removed" not in content
    assert "inline comment should be removed" not in content
    assert "hash inside string should stay" in content

