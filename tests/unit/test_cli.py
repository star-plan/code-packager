"""
CommandLineInterface（argparse 包装层）的单元测试。

注意：
- argparse 对 --help/--version 会直接触发 SystemExit，这属于正常行为；
  测试里用 pytest.raises(SystemExit) 进行断言。
- 这里主要验证“解析”和“validate_arguments”的逻辑是否符合预期。
"""

from __future__ import annotations

import pytest

from code_packager.cli import CommandLineInterface


def test_validate_arguments_allows_list_presets_without_positional_args() -> None:
    """
    --list-presets 场景不要求提供 source_dir/output_zip。
    """

    cli = CommandLineInterface()
    args = cli.parse_arguments(["--list-presets"])
    ok, msg = cli.validate_arguments(args)

    assert ok is True
    assert msg == ""


def test_validate_arguments_requires_source_and_output_when_not_listing_presets() -> None:
    """
    未提供位置参数时应提示错误。
    """

    cli = CommandLineInterface()
    args = cli.parse_arguments([])
    ok, msg = cli.validate_arguments(args)

    assert ok is False
    assert "请提供源代码目录" in msg


def test_parse_arguments_accepts_compression_choice() -> None:
    """
    --compression 只能是预定义选项，合法选项应能解析出来。
    """

    cli = CommandLineInterface()
    args = cli.parse_arguments([".", "out.zip", "--compression", "lzma"])

    assert args.source_dir == "."
    assert args.output_zip == "out.zip"
    assert args.compression == "lzma"


def test_version_flag_exits_and_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    """
    argparse 的 version action 会打印版本并抛出 SystemExit(0)。
    """

    cli = CommandLineInterface()
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_arguments(["--version"])

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    # 输出通常形如：pack-my-code 0.2.0\n
    assert "0.2.0" in captured.out


def test_help_flag_exits(capsys: pytest.CaptureFixture[str]) -> None:
    """
    --help 会打印帮助并退出（SystemExit(0)）。
    """

    cli = CommandLineInterface()
    with pytest.raises(SystemExit) as exc_info:
        cli.parse_arguments(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "示例用法" in captured.out

