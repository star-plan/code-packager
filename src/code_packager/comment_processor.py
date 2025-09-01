"""注释处理模块

负责处理各种编程语言的注释和文档字符串移除。
"""

import re
from typing import List
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
    
    def _is_docstring_start(self, lines: List[str], line_index: int) -> bool:
        """检查指定行是否是docstring的开始
        
        Args:
            lines (List[str]): 代码行列表
            line_index (int): 当前行索引
            
        Returns:
            bool: 是否是docstring开始
        """
        if line_index >= len(lines):
            return False
        
        line = lines[line_index].strip()
        if not (line.startswith('"""') or line.startswith("'''")):
            return False
        
        # 检查是否是模块级别的docstring（文件开头或只有注释/空行之前）
        is_module_start = True
        for i in range(line_index):
            prev_line = lines[i].strip()
            if prev_line and not prev_line.startswith('#'):
                # 如果前面有非注释、非空行的代码，则不是模块级docstring
                is_module_start = False
                break
        
        if is_module_start:
            return True
        
        # 向前查找最近的非空、非注释行
        for i in range(line_index - 1, -1, -1):
            prev_line = lines[i].strip()
            if not prev_line:  # 跳过空行
                continue
            if prev_line.startswith('#'):  # 跳过注释行
                continue
            
            # 检查是否是函数、类定义
            if (prev_line.startswith('def ') or 
                prev_line.startswith('class ') or 
                prev_line.startswith('async def ') or
                prev_line.endswith(':')):
                return True
            
            # 如果遇到其他代码，则不是docstring
            return False
        
        return False
    
    def _remove_python_comments(self, content: str) -> str:
        """移除Python代码中的注释和docstring
        
        Args:
            content (str): Python代码内容
            
        Returns:
            str: 处理后的内容
        """
        lines = content.split('\n')
        result_lines = []
        in_multiline_string = False
        in_docstring = False
        string_delimiter = None
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped:
                result_lines.append(line)
                i += 1
                continue
            
            # 如果在多行字符串或docstring中
            if in_multiline_string or in_docstring:
                if string_delimiter and string_delimiter in line:
                    # 检查是否是字符串结束
                    if line.count(string_delimiter) % 2 == 1:
                        if in_docstring:
                            # docstring结束，跳过这一行
                            in_docstring = False
                            string_delimiter = None
                            i += 1
                            continue
                        else:
                            # 普通多行字符串结束
                            in_multiline_string = False
                            string_delimiter = None
                            result_lines.append(line)
                
                # 如果是docstring，跳过这一行
                if in_docstring:
                    i += 1
                    continue
                else:
                    result_lines.append(line)
                i += 1
                continue
            
            # 检查是否是docstring开始
            if self._is_docstring_start(lines, i):
                string_delimiter = stripped[:3] if stripped.startswith(('"""', "'''")) else None
                if string_delimiter:
                    # 检查是否是单行docstring
                    if stripped.count(string_delimiter) >= 2:
                        # 单行docstring，直接跳过
                        i += 1
                        continue
                    else:
                        # 多行docstring开始
                        in_docstring = True
                        i += 1
                        continue
            
            # 检查是否是普通多行字符串
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                string_delimiter = stripped[:3]
                if stripped.count(string_delimiter) == 1:
                    in_multiline_string = True
                result_lines.append(line)
                i += 1
                continue
            
            # 处理单行注释
            elif stripped.startswith('#'):
                i += 1
                continue
            
            else:
                # 处理行内注释
                comment_pos = line.find('#')
                if comment_pos != -1:
                    # 简单处理，不考虑字符串内的#
                    line = line[:comment_pos].rstrip()
                if line.strip():  # 只保留非空行
                    result_lines.append(line)
                i += 1
                continue
            
            i += 1
        
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