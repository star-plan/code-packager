"""文件过滤模块

负责处理文件和目录的排除逻辑。
"""

import os
from typing import Optional
from pathspec import PathSpec
from loguru import logger


class FileFilter:
    """文件过滤类
    
    负责处理文件和目录的排除逻辑，支持全局规则和局部.gitignore规则。
    """
    
    def __init__(self, global_pathspec: PathSpec):
        """初始化文件过滤器
        
        Args:
            global_pathspec (PathSpec): 全局路径匹配规则
        """
        self.global_pathspec = global_pathspec
    
    def load_gitignore_patterns(self, dir_path: str) -> Optional[PathSpec]:
        """加载当前目录下的 .gitignore 文件规则
        
        Args:
            dir_path (str): 目录路径
            
        Returns:
            Optional[PathSpec]: .gitignore规则对象，如果文件不存在则返回None
        """
        gitignore_path = os.path.join(dir_path, '.gitignore')
        if not os.path.exists(gitignore_path):
            return None
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                return PathSpec.from_lines('gitwildmatch', f)
        except Exception as e:
            logger.warning(f"读取.gitignore文件失败 {gitignore_path}: {e}")
            return None
    
    def should_exclude(self, file_path: str, source_dir: str, 
                      local_pathspec: Optional[PathSpec] = None) -> bool:
        """判断是否应该排除文件或目录
        
        Args:
            file_path (str): 文件或目录的完整路径
            source_dir (str): 源目录路径
            local_pathspec (Optional[PathSpec]): 局部规则（如.gitignore）
            
        Returns:
            bool: 是否应该排除
        """
        try:
            relative_path = os.path.relpath(file_path, start=source_dir)
            
            # 全局规则检查
            if self.global_pathspec.match_file(relative_path):
                return True
            
            # 局部规则检查 (.gitignore)
            if local_pathspec and local_pathspec.match_file(relative_path):
                return True
            
            return False
        except Exception as e:
            logger.warning(f"检查文件排除规则时出错 {file_path}: {e}")
            return False
    
    def filter_directories(self, dirs: list, root: str, source_dir: str, 
                          local_pathspec: Optional[PathSpec] = None) -> list:
        """过滤需要排除的目录
        
        Args:
            dirs (list): 目录列表（会被就地修改）
            root (str): 当前根目录
            source_dir (str): 源目录路径
            local_pathspec (Optional[PathSpec]): 局部规则（如.gitignore）
            
        Returns:
            list: 过滤后的目录列表
        """
        filtered_dirs = []
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not self.should_exclude(dir_path, source_dir, local_pathspec):
                filtered_dirs.append(d)
            else:
                logger.debug(f"已排除目录: {os.path.relpath(dir_path, start=source_dir)}")
        
        return filtered_dirs
    
    def should_include_file(self, file_path: str, source_dir: str, 
                           local_pathspec: Optional[PathSpec] = None) -> bool:
        """判断是否应该包含文件
        
        Args:
            file_path (str): 文件的完整路径
            source_dir (str): 源目录路径
            local_pathspec (Optional[PathSpec]): 局部规则（如.gitignore）
            
        Returns:
            bool: 是否应该包含文件
        """
        return not self.should_exclude(file_path, source_dir, local_pathspec)
    
    def get_relative_path(self, file_path: str, source_dir: str) -> str:
        """获取文件相对于源目录的相对路径
        
        Args:
            file_path (str): 文件的完整路径
            source_dir (str): 源目录路径
            
        Returns:
            str: 相对路径
        """
        try:
            return os.path.relpath(file_path, start=source_dir)
        except Exception as e:
            logger.warning(f"获取相对路径失败 {file_path}: {e}")
            return file_path