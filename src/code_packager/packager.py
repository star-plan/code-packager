"""压缩包管理模块

负责核心的文件打包和压缩逻辑。
"""

import os
import zipfile
from pathlib import Path
from typing import Dict, Any
from pathspec import PathSpec
from loguru import logger

from .file_filter import FileFilter
from .comment_processor import CommentProcessor


class CodePackager:
    """代码打包器类
    
    负责将源代码目录打包成压缩文件，支持文件过滤和注释移除。
    """
    
    # 压缩方法映射
    COMPRESSION_METHODS = {
        'deflate': zipfile.ZIP_DEFLATED,
        'lzma': zipfile.ZIP_LZMA,
        'bzip2': zipfile.ZIP_BZIP2
    }
    
    def __init__(self, global_pathspec: PathSpec):
        """初始化代码打包器
        
        Args:
            global_pathspec (PathSpec): 全局路径匹配规则
        """
        self.file_filter = FileFilter(global_pathspec)
        self.comment_processor = CommentProcessor()
        self._stats = self._init_stats()
    
    def _init_stats(self) -> Dict[str, int]:
        """初始化统计信息
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        return {
            'total_files': 0,
            'included_files': 0,
            'excluded_files': 0,
            'total_size': 0,
            'compressed_size': 0,
            'files_with_comments_removed': 0
        }
    
    def get_compression_method(self, method_name: str) -> int:
        """获取压缩方法常量
        
        Args:
            method_name (str): 压缩方法名称
            
        Returns:
            int: zipfile压缩方法常量
        """
        return self.COMPRESSION_METHODS.get(method_name, zipfile.ZIP_DEFLATED)
    
    def _process_file_content(self, file_path: str, remove_comments: bool) -> tuple[bytes, bool]:
        """处理文件内容
        
        Args:
            file_path (str): 文件路径
            remove_comments (bool): 是否移除注释
            
        Returns:
            tuple[bytes, bool]: (文件内容字节, 是否处理了注释)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if remove_comments:
                file_ext = Path(file_path).suffix.lower()
                processed_content, was_modified = self.comment_processor.process_file_content(
                    content, file_ext
                )
                return processed_content.encode('utf-8'), was_modified
            else:
                return content.encode('utf-8'), False
                
        except UnicodeDecodeError:
            # 对于二进制文件，直接读取原始字节
            with open(file_path, 'rb') as f:
                return f.read(), False
        except Exception as e:
            logger.warning(f"无法处理文件 {file_path}: {e}，使用原文件")
            try:
                with open(file_path, 'rb') as f:
                    return f.read(), False
            except Exception as e2:
                logger.error(f"读取文件失败 {file_path}: {e2}")
                return b'', False
    
    def _add_file_to_zip(self, zf: zipfile.ZipFile, file_path: str, arcname: str, 
                        remove_comments: bool) -> None:
        """将文件添加到压缩包
        
        Args:
            zf (zipfile.ZipFile): 压缩文件对象
            file_path (str): 源文件路径
            arcname (str): 压缩包内的文件名
            remove_comments (bool): 是否移除注释
        """
        try:
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            self._stats['total_size'] += file_size
            
            if remove_comments:
                content_bytes, was_modified = self._process_file_content(file_path, True)
                if was_modified:
                    self._stats['files_with_comments_removed'] += 1
                # 将处理后的内容写入压缩包
                zf.writestr(arcname, content_bytes)
            else:
                # 直接添加原文件
                zf.write(file_path, arcname)
            
            self._stats['included_files'] += 1
            logger.debug(f"已添加: {arcname} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"添加文件到压缩包失败 {file_path}: {e}")
    
    def create_zip(self, source_dir: str, output_zip: str, 
                  remove_comments: bool = False, 
                  compression_method: str = 'deflate') -> Dict[str, Any]:
        """创建压缩包，排除指定的文件和目录
        
        Args:
            source_dir (str): 源目录路径
            output_zip (str): 输出压缩包路径
            remove_comments (bool): 是否移除注释
            compression_method (str): 压缩方法
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        # 重置统计信息
        self._stats = self._init_stats()
        
        # 获取压缩方法
        compression = self.get_compression_method(compression_method)
        
        logger.info(f"开始打包: {source_dir} -> {output_zip}")
        logger.info(f"压缩方法: {compression_method}")
        logger.info(f"去除注释: {'是' if remove_comments else '否'}")
        
        try:
            with zipfile.ZipFile(output_zip, 'w', compression, allowZip64=True) as zf:
                for root, dirs, files in os.walk(source_dir):
                    # 加载当前目录的 .gitignore 规则
                    gitignore_spec = self.file_filter.load_gitignore_patterns(root)
                    
                    # 过滤需要排除的目录
                    dirs[:] = self.file_filter.filter_directories(
                        dirs, root, source_dir, gitignore_spec
                    )
                    
                    # 处理文件
                    for file in files:
                        file_path = os.path.join(root, file)
                        self._stats['total_files'] += 1
                        
                        if self.file_filter.should_include_file(
                            file_path, source_dir, gitignore_spec
                        ):
                            arcname = self.file_filter.get_relative_path(file_path, source_dir)
                            self._add_file_to_zip(zf, file_path, arcname, remove_comments)
                        else:
                            self._stats['excluded_files'] += 1
                            relative_path = self.file_filter.get_relative_path(file_path, source_dir)
                            logger.debug(f"已排除: {relative_path}")
            
            # 获取压缩后大小
            self._stats['compressed_size'] = os.path.getsize(output_zip)
            
            logger.info(f"打包完成，共处理 {self._stats['total_files']} 个文件")
            return self._stats.copy()
            
        except Exception as e:
            logger.error(f"创建压缩包时发生错误: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """获取当前统计信息
        
        Returns:
            Dict[str, Any]: 统计信息副本
        """
        return self._stats.copy()