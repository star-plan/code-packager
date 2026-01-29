"""
actions.run_packaging_task() 的集成测试。

它相当于 CLI/TUI 共享的“业务入口”，覆盖点：
- 输入目录校验失败时返回 False
- 正常输入时返回 True 并生成 zip
- 指定 config_path 时按配置规则工作（这也会驱动修复当前实现中的缺陷）
"""

from __future__ import annotations

from pathlib import Path

from code_packager.actions import run_packaging_task


def test_run_packaging_task_returns_false_for_missing_source_dir(tmp_path: Path) -> None:
    """
    源目录不存在，应直接失败。
    """

    missing = tmp_path / "missing"
    output_zip = tmp_path / "out.zip"

    ok = run_packaging_task(str(missing), str(output_zip))
    assert ok is False
    assert output_zip.exists() is False


def test_run_packaging_task_creates_zip_for_valid_source(tmp_path: Path) -> None:
    """
    正常目录应能生成 zip。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")

    output_zip = tmp_path / "out.zip"
    ok = run_packaging_task(str(source_dir), str(output_zip), preset="basic", remove_comments=False)

    assert ok is True
    assert output_zip.exists() is True


def test_run_packaging_task_uses_custom_config_file(tmp_path: Path) -> None:
    """
    传入 config_path 时应使用该文件中的规则。

    本用例构造规则：排除 *.txt，只留下 main.py。
    """

    source_dir = tmp_path / "repo"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (source_dir / "note.txt").write_text("should be excluded\n", encoding="utf-8")

    config_file = tmp_path / "rules.conf"
    config_file.write_text("*.txt\n", encoding="utf-8")

    output_zip = tmp_path / "out.zip"
    ok = run_packaging_task(str(source_dir), str(output_zip), config_path=str(config_file), remove_comments=False)

    assert ok is True
    assert output_zip.exists() is True

