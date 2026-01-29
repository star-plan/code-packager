"""
docstring 去除功能测试（pytest 版本）。

历史说明：
- 仓库原先的 tests/test_docstring_removal.py 更像“手工运行脚本”，且导入目标函数不存在。
- 这里改为 pytest 可收集的断言式测试，并将测试对象改为 CommentProcessor。
"""

from __future__ import annotations

from code_packager.comment_processor import CommentProcessor


def test_remove_docstrings_from_functions_and_classes() -> None:
    """
    断言函数/类/方法 docstring 会被移除，同时普通字符串应被保留。
    """

    source = '''def load_gitignore_patterns(dir_path):
    """加载当前目录下的 .gitignore 文件规则"""
    gitignore_path = os.path.join(dir_path, '.gitignore')
    if os.path.exists(gitignore_path):
        return load_pathspec_from_file(gitignore_path)
    return None

class TestClass:
    """这是一个测试类

    用于演示多行docstring的处理
    """

    def __init__(self):
        # 这是一个普通注释
        self.value = "这是一个字符串"  # 行内注释

    def method_with_docstring(self):
        """这是方法的docstring"""
        return True

    def method_with_multiline_docstring(self):
        """
        这是多行docstring
        包含多行内容
        """
        # 普通注释
        normal_string = """这不是docstring，是普通字符串"""
        return normal_string
'''

    processor = CommentProcessor()
    cleaned = processor.remove_comments_from_content(source, ".py")

    # docstring 应被移除
    assert "加载当前目录下的 .gitignore 文件规则" not in cleaned
    assert "这是一个测试类" not in cleaned
    assert "这是方法的docstring" not in cleaned
    assert "这是多行docstring" not in cleaned

    # 普通字符串应保留
    assert "这不是docstring，是普通字符串" in cleaned


def test_remove_module_docstring() -> None:
    """
    断言模块级 docstring 会被移除。
    """

    source = '''"""这是模块级docstring
应该被去除
"""

import os

def some_function():
    """函数docstring"""
    pass
'''

    processor = CommentProcessor()
    cleaned = processor.remove_comments_from_content(source, ".py")

    assert "这是模块级docstring" not in cleaned
    assert "函数docstring" not in cleaned
