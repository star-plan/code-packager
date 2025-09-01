"""注释处理模块

负责处理各种编程语言的注释和文档字符串移除。
使用 Python 内置的 tokenize 模块实现更准确的注释处理。
"""

import io
import re
import tokenize
from typing import List, Optional
from loguru import logger


class CommentProcessor:
    """注释处理类
    
    负责处理各种编程语言的注释和文档字符串移除。
    """
    
    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.ts', '.jsx', '.tsx'],
        'c_family': ['.java', '.c', '.cpp', '.h']
    }
    
    def __init__(self):
        """初始化注释处理器"""
        pass
    
    def is_supported_file(self, file_extension: str) -> bool:
        """检查文件扩展名是否支持注释移除
        
        Args:
            file_extension (str): 文件扩展名
            
        Returns:
            bool: 是否支持注释移除
        """
        for extensions in self.SUPPORTED_EXTENSIONS.values():
            if file_extension.lower() in extensions:
                return True
        return False
    
    def remove_comments_from_content(self, content: str, file_extension: str) -> str:
        """根据文件类型去除代码注释和文档字符串
        
        Args:
            content (str): 文件内容
            file_extension (str): 文件扩展名
            
        Returns:
            str: 处理后的内容
        """
        if file_extension in self.SUPPORTED_EXTENSIONS['python']:
            return self._remove_python_comments(content)
        elif file_extension in (self.SUPPORTED_EXTENSIONS['javascript'] + 
                               self.SUPPORTED_EXTENSIONS['c_family']):
            return self._remove_c_style_comments(content)
        
        return content
    
    def _remove_python_comments(self, content: str) -> str:
        """移除Python代码中的注释和docstring
        
        使用 tokenize 模块实现更准确的注释和文档字符串移除。
        
        Args:
            content (str): Python代码内容
            
        Returns:
            str: 处理后的内容
        """
        try:
            return self._remove_comments_and_docstrings_with_tokenize(content)
        except Exception as e:
            logger.warning(f"使用 tokenize 处理失败，回退到简单处理: {e}")
            return self._simple_remove_python_comments(content)
    
    def _remove_comments_and_docstrings_with_tokenize(self, source: str) -> str:
        """使用 tokenize 模块移除注释和文档字符串
        
        Args:
            source (str): Python 源代码
            
        Returns:
            str: 处理后的代码
        """
        io_obj = io.StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        
        try:
            for tok in tokenize.generate_tokens(io_obj.readline):
                token_type = tok[0]
                token_string = tok[1]
                start_line, start_col = tok[2]
                end_line, end_col = tok[3]
                ltext = tok[4]
                
                # 处理换行
                if start_line > last_lineno:
                    last_col = 0
                if start_col > last_col:
                    out += (" " * (start_col - last_col))
                
                # 跳过注释
                if token_type == tokenize.COMMENT:
                    pass
                # 跳过文档字符串
                elif token_type == tokenize.STRING:
                    if prev_toktype != tokenize.INDENT:
                        # 如果前一个token不是缩进，说明这是一个普通字符串
                        if prev_toktype != tokenize.NEWLINE:
                            if start_col > 0:
                                out += token_string
                else:
                    out += token_string
                
                prev_toktype = token_type
                last_col = end_col
                last_lineno = end_line
                
        except tokenize.TokenError:
            # 如果tokenize失败，返回原始内容
            return source
            
        return out
    
    def _simple_remove_python_comments(self, content: str) -> str:
        """简单的Python注释移除（回退方案）
        
        Args:
            content (str): Python代码内容
            
        Returns:
            str: 处理后的内容
        """
        lines = content.split('\n')
        result_lines = []
        
        for line in lines:
            # 简单移除以 # 开头的注释行
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # 移除行内注释（简单处理，不考虑字符串内的#）
            if '#' in line:
                # 查找第一个不在字符串内的#
                in_string = False
                quote_char = None
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                    elif char == '#' and not in_string:
                        line = line[:i].rstrip()
                        break
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _remove_c_style_comments(self, content: str) -> str:
        """移除C风格语言的注释（JavaScript/TypeScript/Java/C/C++）
        
        Args:
            content (str): 代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 简单实现，去除//和/* */注释
        # 移除单行注释
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # 移除多行注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def process_file_content(self, content: str, file_extension: str) -> tuple[str, bool]:
        """处理文件内容，移除注释
        
        Args:
            content (str): 原始文件内容
            file_extension (str): 文件扩展名
            
        Returns:
            tuple[str, bool]: (处理后的内容, 是否有修改)
        """
        if not self.is_supported_file(file_extension):
            return content, False
        
        try:
            processed_content = self.remove_comments_from_content(content, file_extension)
            return processed_content, processed_content != content
        except Exception as e:
            logger.warning(f"处理文件内容时出错: {e}")
            return content, False