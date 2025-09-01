"""注释处理模块

负责处理各种编程语言的注释和文档字符串移除。
使用 Python 内置的 tokenize 模块实现更准确的注释处理。
"""

import copy
import io
import re
import token
import tokenize
from typing import List, Optional, Tuple
from loguru import logger


class CommentProcessor:
    """注释处理类
    
    负责处理各种编程语言的注释和文档字符串移除。
    """
    
    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {
        'python': ['.py', '.pyw'],
        'javascript': ['.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs'],
        'c_family': ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx'],
        'java': ['.java'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php', '.phtml', '.php3', '.php4', '.php5', '.phps'],
        'ruby': ['.rb', '.rbw'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala', '.sc'],
        'shell': ['.sh', '.bash', '.zsh', '.fish'],
        'perl': ['.pl', '.pm'],
        'r': ['.r', '.R'],
        'matlab': ['.m'],
        'lua': ['.lua'],
        'dart': ['.dart'],
        'elixir': ['.ex', '.exs'],
        'erlang': ['.erl', '.hrl'],
        'haskell': ['.hs', '.lhs'],
        'clojure': ['.clj', '.cljs', '.cljc'],
        'fsharp': ['.fs', '.fsx', '.fsi'],
        'csharp': ['.cs'],
        'vb': ['.vb'],
        'sql': ['.sql'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'html': ['.html', '.htm', '.xhtml'],
        'xml': ['.xml', '.xsl', '.xslt']
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
        # Python 语言
        if file_extension in self.SUPPORTED_EXTENSIONS['python']:
            return self._remove_python_comments(content)
        
        # C 风格注释语言 (// 和 /* */)
        elif file_extension in (self.SUPPORTED_EXTENSIONS['javascript'] + 
                               self.SUPPORTED_EXTENSIONS['c_family'] +
                               self.SUPPORTED_EXTENSIONS['java'] +
                               self.SUPPORTED_EXTENSIONS['go'] +
                               self.SUPPORTED_EXTENSIONS['rust'] +
                               self.SUPPORTED_EXTENSIONS['swift'] +
                               self.SUPPORTED_EXTENSIONS['kotlin'] +
                               self.SUPPORTED_EXTENSIONS['scala'] +
                               self.SUPPORTED_EXTENSIONS['dart'] +
                               self.SUPPORTED_EXTENSIONS['csharp'] +
                               self.SUPPORTED_EXTENSIONS['css']):
            return self._remove_c_style_comments(content)
        
        # PHP 语言 (支持 #, // 和 /* */)
        elif file_extension in self.SUPPORTED_EXTENSIONS['php']:
            return self._remove_php_comments(content)
        
        # Ruby 语言 (# 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['ruby']:
            return self._remove_hash_comments(content)
        
        # Shell 脚本 (# 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['shell']:
            return self._remove_hash_comments(content)
        
        # Perl 语言 (# 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['perl']:
            return self._remove_hash_comments(content)
        
        # R 语言 (# 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['r']:
            return self._remove_hash_comments(content)
        
        # MATLAB 语言 (% 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['matlab']:
            return self._remove_matlab_comments(content)
        
        # Lua 语言 (-- 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['lua']:
            return self._remove_lua_comments(content)
        
        # Haskell 语言 (-- 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['haskell']:
            return self._remove_haskell_comments(content)
        
        # SQL 语言 (-- 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['sql']:
            return self._remove_sql_comments(content)
        
        # HTML/XML 语言 (<!-- --> 注释)
        elif file_extension in (self.SUPPORTED_EXTENSIONS['html'] +
                               self.SUPPORTED_EXTENSIONS['xml']):
            return self._remove_html_comments(content)
        
        # Visual Basic 语言 (' 注释)
        elif file_extension in self.SUPPORTED_EXTENSIONS['vb']:
            return self._remove_vb_comments(content)
        
        # 其他语言暂不处理
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
        """
        使用简单但可靠的方法移除 Python 注释和文档字符串
        """
        try:
            import re
            
            # 首先移除单行注释（# 开头的注释）
            lines = source.splitlines()
            result_lines = []
            
            for line in lines:
                # 查找注释位置（不在字符串内的 #）
                in_string = False
                string_char = None
                escaped = False
                comment_pos = -1
                
                for i, char in enumerate(line):
                    if escaped:
                        escaped = False
                        continue
                    
                    if char == '\\':
                        escaped = True
                        continue
                    
                    if not in_string:
                        if char in ['"', "'"]:
                            in_string = True
                            string_char = char
                        elif char == '#':
                            comment_pos = i
                            break
                    else:
                        if char == string_char:
                            in_string = False
                            string_char = None
                
                if comment_pos >= 0:
                    result_lines.append(line[:comment_pos].rstrip())
                else:
                    result_lines.append(line)
            
            # 重新组合代码
            code_without_comments = '\n'.join(result_lines)
            
            # 移除文档字符串（三引号字符串）
            # 移除三重双引号文档字符串
            code_without_comments = re.sub(
                r'(^|\n)\s*"""[\s\S]*?"""\s*(?=\n|$)',
                '',
                code_without_comments,
                flags=re.MULTILINE
            )
            
            # 移除三重单引号文档字符串
            code_without_comments = re.sub(
                r"(^|\n)\s*'''[\s\S]*?'''\s*(?=\n|$)",
                '',
                code_without_comments,
                flags=re.MULTILINE
            )
            
            # 清理多余的空行
            lines = code_without_comments.split('\n')
            cleaned_lines = []
            prev_empty = False
            
            for line in lines:
                is_empty = not line.strip()
                if is_empty and prev_empty:
                    continue  # 跳过连续的空行
                cleaned_lines.append(line)
                prev_empty = is_empty
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            self.logger.warning(f"注释移除处理失败: {e}，使用简单方法")
            return self._simple_remove_python_comments(source)
    
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
        """移除C风格语言的注释（JavaScript/TypeScript/Java/C/C++/Go/Rust等）
        
        Args:
            content (str): 代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除单行注释 (//)
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # 移除多行注释 (/* */)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _remove_php_comments(self, content: str) -> str:
        """移除PHP注释（支持 #, // 和 /* */）
        
        Args:
            content (str): PHP代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除 # 注释
        content = re.sub(r'#.*?$', '', content, flags=re.MULTILINE)
        # 移除 // 注释
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # 移除 /* */ 注释
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _remove_hash_comments(self, content: str) -> str:
        """移除使用 # 的注释（Ruby/Shell/Perl/R等）
        
        Args:
            content (str): 代码内容
            
        Returns:
            str: 处理后的内容
        """
        lines = content.splitlines()
        result_lines = []
        
        for line in lines:
            # 查找注释位置（不在字符串内的 #）
            in_string = False
            string_char = None
            escaped = False
            comment_pos = -1
            
            for i, char in enumerate(line):
                if escaped:
                    escaped = False
                    continue
                
                if char == '\\':
                    escaped = True
                    continue
                
                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        string_char = char
                    elif char == '#':
                        comment_pos = i
                        break
                else:
                    if char == string_char:
                        in_string = False
                        string_char = None
            
            if comment_pos >= 0:
                result_lines.append(line[:comment_pos].rstrip())
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _remove_matlab_comments(self, content: str) -> str:
        """移除MATLAB注释（% 注释）
        
        Args:
            content (str): MATLAB代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除 % 注释
        content = re.sub(r'%.*?$', '', content, flags=re.MULTILINE)
        return content
    
    def _remove_lua_comments(self, content: str) -> str:
        """移除Lua注释（-- 注释和 --[[ ]] 多行注释）
        
        Args:
            content (str): Lua代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除多行注释 --[[ ]]
        content = re.sub(r'--\[\[.*?\]\]', '', content, flags=re.DOTALL)
        # 移除单行注释 --
        content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)
        return content
    
    def _remove_haskell_comments(self, content: str) -> str:
        """移除Haskell注释（-- 注释和 {- -} 多行注释）
        
        Args:
            content (str): Haskell代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除多行注释 {- -}
        content = re.sub(r'\{-.*?-\}', '', content, flags=re.DOTALL)
        # 移除单行注释 --
        content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)
        return content
    
    def _remove_sql_comments(self, content: str) -> str:
        """移除SQL注释（-- 注释和 /* */ 多行注释）
        
        Args:
            content (str): SQL代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除多行注释 /* */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # 移除单行注释 --
        content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)
        return content
    
    def _remove_html_comments(self, content: str) -> str:
        """移除HTML/XML注释（<!-- --> 注释）
        
        Args:
            content (str): HTML/XML代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除 HTML/XML 注释 <!-- -->
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        return content
    
    def _remove_vb_comments(self, content: str) -> str:
        """移除Visual Basic注释（' 注释）
        
        Args:
            content (str): VB代码内容
            
        Returns:
            str: 处理后的内容
        """
        # 移除 ' 注释
        content = re.sub(r'\'.*?$', '', content, flags=re.MULTILINE)
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