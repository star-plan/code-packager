#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试docstring去除功能的脚本
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from code_packager.main import remove_comments_from_content

def test_docstring_removal():
    """测试docstring去除功能"""
    
    # 测试代码示例1：函数和类的docstring
    test_code1 = '''def load_gitignore_patterns(dir_path):
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
    
    # 测试代码示例2：模块级docstring
    test_code2 = '''"""这是模块级docstring
应该被去除
"""

import os

def some_function():
    """函数docstring"""
    pass
'''
    
    print("测试1 - 函数和类docstring:")
    print("=" * 50)
    print("原始代码:")
    print(test_code1)
    
    cleaned_code1 = remove_comments_from_content(test_code1, '.py')
    print("\n去除注释和docstring后:")
    print(cleaned_code1)
    
    # 验证函数和类docstring是否被去除
    docstring_removed1 = ('加载当前目录下的 .gitignore 文件规则' not in cleaned_code1 and
                         '这是一个测试类' not in cleaned_code1 and
                         '这是方法的docstring' not in cleaned_code1 and
                         '这是多行docstring' not in cleaned_code1)
    
    normal_string_kept1 = '这不是docstring，是普通字符串' in cleaned_code1
    
    print(f"\n函数/类docstring去除: {'✅ 通过' if docstring_removed1 else '❌ 失败'}")
    print(f"普通字符串保留: {'✅ 通过' if normal_string_kept1 else '❌ 失败'}")
    
    print("\n" + "=" * 70)
    print("测试2 - 模块级docstring:")
    print("=" * 50)
    print("原始代码:")
    print(test_code2)
    
    cleaned_code2 = remove_comments_from_content(test_code2, '.py')
    print("\n去除注释和docstring后:")
    print(cleaned_code2)
    
    # 验证模块级docstring是否被去除
    module_docstring_removed = '这是模块级docstring' not in cleaned_code2
    function_docstring_removed = '函数docstring' not in cleaned_code2
    
    print(f"\n模块级docstring去除: {'✅ 通过' if module_docstring_removed else '❌ 失败'}")
    print(f"函数docstring去除: {'✅ 通过' if function_docstring_removed else '❌ 失败'}")
    
    # 总结
    all_tests_passed = (docstring_removed1 and normal_string_kept1 and 
                       module_docstring_removed and function_docstring_removed)
    
    print("\n" + "=" * 70)
    print(f"总体测试结果: {'✅ 全部通过' if all_tests_passed else '❌ 部分失败'}")

if __name__ == "__main__":
    test_docstring_removal()