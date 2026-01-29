"""
main.main() 的路由逻辑测试。

约束：
- main() 的逻辑是：sys.argv 长度 > 1 则走 run_cli()，否则 run_tui()。
- 这里不测试 TUI/CLI 的具体行为，只测试“分发”是否正确。
"""

from __future__ import annotations

from typing import List

from code_packager import main as main_module


def test_main_routes_to_tui_when_no_args(monkeypatch) -> None:
    """
    sys.argv 只有脚本名时，应调用 run_tui()。
    """

    called: List[str] = []

    def fake_run_tui() -> None:
        called.append("tui")

    def fake_run_cli() -> None:
        called.append("cli")

    monkeypatch.setattr(main_module, "run_tui", fake_run_tui)
    monkeypatch.setattr(main_module, "run_cli", fake_run_cli)
    monkeypatch.setattr(main_module.sys, "argv", ["pack-my-code"])

    main_module.main()
    assert called == ["tui"]


def test_main_routes_to_cli_when_has_args(monkeypatch) -> None:
    """
    sys.argv 除脚本名外还有参数时，应调用 run_cli()。
    """

    called: List[str] = []

    def fake_run_tui() -> None:
        called.append("tui")

    def fake_run_cli() -> None:
        called.append("cli")

    monkeypatch.setattr(main_module, "run_tui", fake_run_tui)
    monkeypatch.setattr(main_module, "run_cli", fake_run_cli)
    monkeypatch.setattr(main_module.sys, "argv", ["pack-my-code", "."])

    main_module.main()
    assert called == ["cli"]

