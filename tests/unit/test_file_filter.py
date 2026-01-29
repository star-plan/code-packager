"""
FileFilter 的单元测试。

重点验证：
- 全局 PathSpec 排除规则是否生效
- 根目录 .gitignore 生成的局部 PathSpec 是否生效
- filter_directories() 对 os.walk 的 dirs[:] 过滤逻辑是否正确
"""

from __future__ import annotations

import os
from pathlib import Path

from pathspec import PathSpec

from code_packager.file_filter import FileFilter


def test_should_exclude_matches_global_rules(tmp_path: Path) -> None:
    """
    全局规则通过 relative_path（相对 source_dir）进行匹配。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()

    # 构造一些文件
    log_file = source_dir / "debug.log"
    py_file = source_dir / "main.py"
    log_file.write_text("log", encoding="utf-8")
    py_file.write_text("print('hi')", encoding="utf-8")

    global_spec = PathSpec.from_lines("gitwildmatch", ["*.log"])
    ff = FileFilter(global_spec)

    assert ff.should_exclude(str(log_file), str(source_dir)) is True
    assert ff.should_exclude(str(py_file), str(source_dir)) is False


def test_load_gitignore_patterns_and_should_exclude(tmp_path: Path) -> None:
    """
    根目录下的 .gitignore 应能被 load_gitignore_patterns() 加载并生效。

    注意：当前实现用 relative_path=relpath(file_path, source_dir) 做局部匹配，
    因此这里选择“根目录 .gitignore”的场景来做稳定断言。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()

    # 目录/文件结构
    node_modules = source_dir / "node_modules"
    node_modules.mkdir()
    (node_modules / "lib.js").write_text("console.log(1)", encoding="utf-8")

    src_dir = source_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("print(1)", encoding="utf-8")

    # .gitignore 排除 node_modules/
    (source_dir / ".gitignore").write_text("node_modules/\n", encoding="utf-8")

    global_spec = PathSpec.from_lines("gitwildmatch", [])
    ff = FileFilter(global_spec)
    local_spec = ff.load_gitignore_patterns(str(source_dir))

    assert local_spec is not None
    assert ff.should_exclude(str(node_modules), str(source_dir), local_spec) is True
    assert ff.should_exclude(str(src_dir), str(source_dir), local_spec) is False


def test_filter_directories_filters_in_place(tmp_path: Path) -> None:
    """
    os.walk 会读取并依赖 dirs[:] 的就地修改。
    当前 FileFilter.filter_directories 返回过滤后的列表，调用方会执行 dirs[:] = returned。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()

    (source_dir / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    (source_dir / "node_modules").mkdir()
    (source_dir / "src").mkdir()

    global_spec = PathSpec.from_lines("gitwildmatch", [])
    ff = FileFilter(global_spec)
    local_spec = ff.load_gitignore_patterns(str(source_dir))

    dirs = ["node_modules", "src"]
    filtered = ff.filter_directories(dirs=dirs, root=str(source_dir), source_dir=str(source_dir), local_pathspec=local_spec)

    assert "node_modules" not in filtered
    assert "src" in filtered


def test_get_relative_path_returns_relpath(tmp_path: Path) -> None:
    """
    在 Windows 上，os.path.relpath 会使用反斜杠；这里不强行要求分隔符，
    只验证返回值能正确表示相对关系。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()
    nested = source_dir / "a" / "b"
    nested.mkdir(parents=True)
    target = nested / "c.txt"
    target.write_text("x", encoding="utf-8")

    global_spec = PathSpec.from_lines("gitwildmatch", [])
    ff = FileFilter(global_spec)
    rel = ff.get_relative_path(str(target), str(source_dir))

    # 规范化后再断言，避免平台差异导致失败
    assert rel.replace("\\", "/") == "a/b/c.txt"
    assert os.path.isabs(rel) is False

