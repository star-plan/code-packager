"""
ConfigManager 的单元测试。

覆盖点（偏“行为”而非“实现细节”）：
- 预设名称列表是否包含关键项
- 非法 preset 的容错行为
- 从不存在的文件加载规则时返回“空规则”
- 从临时配置文件加载规则能影响 PathSpec.match_file()
"""

from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec

from code_packager.config import ConfigManager


def test_get_preset_names_contains_expected_defaults() -> None:
    """
    预设列表属于对外接口的一部分。

    这里不要求顺序一致，只要求关键 preset 名称存在。
    """

    manager = ConfigManager()
    names = manager.get_preset_names()

    assert "basic" in names
    assert "complete" in names
    assert "lightweight" in names


def test_invalid_preset_returns_empty_pathspec() -> None:
    """
    非法 preset 不应该抛异常；当前实现返回空 PathSpec。
    """

    manager = ConfigManager()
    spec = manager.load_pathspec_from_preset("definitely-not-exist")

    assert isinstance(spec, PathSpec)
    assert spec.match_file("any/file.txt") is False


def test_load_pathspec_from_file_missing_returns_empty_pathspec(tmp_path: Path) -> None:
    """
    配置文件不存在时应返回空规则（match_file 恒为 False）。
    """

    manager = ConfigManager()
    spec = manager.load_pathspec_from_file(str(tmp_path / "missing.conf"))

    assert spec.match_file("a.py") is False
    assert spec.match_file("nested/a.py") is False


def test_load_pathspec_from_file_applies_patterns(tmp_path: Path) -> None:
    """
    从文件加载的规则应影响 match_file 结果。

    这里用 gitwildmatch 语法测试：
    - *.log 排除所有 .log 文件
    - build/ 排除 build 目录
    """

    rules_file = tmp_path / "rules.conf"
    rules_file.write_text("*.log\nbuild/\n", encoding="utf-8")

    manager = ConfigManager()
    spec = manager.load_pathspec_from_file(str(rules_file))

    assert spec.match_file("app.log") is True
    assert spec.match_file("build/output.bin") is True
    assert spec.match_file("src/main.py") is False

