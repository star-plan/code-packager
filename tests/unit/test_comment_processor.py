"""
CommentProcessor 的单元测试。

目标：
- 验证不同语言/扩展名的注释移除行为是否符合预期
- 特别关注 Python：# 注释与 docstring 的边界（字符串内的 # 不应被当成注释）
"""

from __future__ import annotations

from code_packager.comment_processor import CommentProcessor


def test_is_supported_file_recognizes_common_extensions() -> None:
    """
    is_supported_file() 用于决定是否对某些文件做注释移除处理。
    """

    cp = CommentProcessor()

    assert cp.is_supported_file(".py") is True
    assert cp.is_supported_file(".ts") is True
    assert cp.is_supported_file(".html") is True
    assert cp.is_supported_file(".unknown") is False


def test_remove_python_comments_and_docstrings_keeps_string_literals() -> None:
    """
    Python 场景下应做到：
    - 移除模块/类/函数 docstring（三引号，独立占行）
    - 移除行内 # 注释（但不应误伤字符串内的 #）
    - 保留普通字符串（包括三引号字符串，只要它不是 docstring 形态）
    """

    source = '''"""模块 docstring：应该被移除"""

import os  # 行内注释：应该被移除

class A:
    """类 docstring：应该被移除"""

    def f(self):
        """函数 docstring：应该被移除"""
        s1 = "# 这是字符串内的 #，不应被当作注释"
        s2 = """这是普通三引号字符串（被赋值），不应被删除"""
        return s1, s2  # return 行注释也应被移除
'''

    cp = CommentProcessor()
    cleaned = cp.remove_comments_from_content(source, ".py")

    # docstring 内容不应存在
    assert "模块 docstring" not in cleaned
    assert "类 docstring" not in cleaned
    assert "函数 docstring" not in cleaned

    # 行内注释文本不应存在
    assert "行内注释" not in cleaned
    assert "return 行注释" not in cleaned

    # 字符串字面量应保留
    assert "这是字符串内的 #，不应被当作注释" in cleaned
    assert "这是普通三引号字符串（被赋值），不应被删除" in cleaned


def test_remove_c_style_comments() -> None:
    """
    C 风格语言（JS/TS/C/C++/Java/Go/Rust 等）应移除：
    - // 单行注释
    - /* */ 多行注释
    """

    source = "int x = 1; // comment\n/* block\ncomment */\nint y = 2;\n"
    cp = CommentProcessor()
    cleaned = cp.remove_comments_from_content(source, ".c")

    assert "// comment" not in cleaned
    assert "block" not in cleaned
    assert "int x = 1;" in cleaned
    assert "int y = 2;" in cleaned


def test_remove_html_comments() -> None:
    """
    HTML/XML 应移除 <!-- -->。
    """

    source = "<div>ok</div><!-- secret --><span>more</span>"
    cp = CommentProcessor()
    cleaned = cp.remove_comments_from_content(source, ".html")

    assert "<!--" not in cleaned
    assert "secret" not in cleaned
    assert "<div>ok</div>" in cleaned
    assert "<span>more</span>" in cleaned
