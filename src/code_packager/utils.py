"""工具函数模块

提供通用的工具函数。
"""

import os
import sys
from loguru import logger


def setup_logger(verbose: bool = False) -> None:
    """设置日志配置
    
    Args:
        verbose (bool): 是否启用详细输出
    """
    # 移除默认的stderr处理器，避免重复输出
    logger.remove()
    
    # 设置控制台输出
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stdout, colorize=True, level=level)
    
    # 设置文件输出
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    logger.add(os.path.join(log_dir, 'file_{time}.log'), level="DEBUG")


def format_size(size_bytes: int) -> str:
    """格式化文件大小显示
    
    Args:
        size_bytes (int): 字节数
        
    Returns:
        str: 格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_source_directory(source_dir: str) -> bool:
    """验证源目录是否有效
    
    Args:
        source_dir (str): 源目录路径
        
    Returns:
        bool: 目录是否有效
    """
    if not os.path.exists(source_dir):
        logger.error(f"源目录不存在: {source_dir}")
        return False
    
    if not os.path.isdir(source_dir):
        logger.error(f"源路径不是目录: {source_dir}")
        return False
    
    return True


def ensure_output_directory(output_path: str) -> bool:
    """确保输出目录存在
    
    Args:
        output_path (str): 输出文件路径
        
    Returns:
        bool: 是否成功创建或目录已存在
    """
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:  # 如果有目录部分
            os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")
        return False


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """计算压缩率
    
    Args:
        original_size (int): 原始大小（字节）
        compressed_size (int): 压缩后大小（字节）
        
    Returns:
        float: 压缩率（百分比）
    """
    if original_size == 0:
        return 0.0
    return (1 - compressed_size / original_size) * 100


def print_statistics(stats: dict, elapsed_time: float, output_path: str, 
                    remove_comments: bool = False) -> None:
    """打印统计信息
    
    Args:
        stats (dict): 统计信息字典
        elapsed_time (float): 处理时间（秒）
        output_path (str): 输出文件路径
        remove_comments (bool): 是否移除了注释
    """
    logger.info("\n" + "=" * 60)
    logger.info("打包完成! 统计信息:")
    logger.info("=" * 60)
    logger.info(f"总文件数量:     {stats['total_files']:,}")
    logger.info(f"包含文件数量:   {stats['included_files']:,}")
    logger.info(f"排除文件数量:   {stats['excluded_files']:,}")
    logger.info(f"原始总大小:     {format_size(stats['total_size'])}")
    logger.info(f"压缩后大小:     {format_size(stats['compressed_size'])}")
    
    if stats['total_size'] > 0:
        compression_ratio = calculate_compression_ratio(
            stats['total_size'], stats['compressed_size']
        )
        logger.info(f"压缩率:         {compression_ratio:.1f}%")
    
    if remove_comments and stats.get('files_with_comments_removed', 0) > 0:
        logger.info(f"去除注释文件:   {stats['files_with_comments_removed']}")
    
    logger.info(f"处理时间:       {elapsed_time:.2f} 秒")
    logger.info(f"输出文件:       {output_path}")
    logger.info("=" * 60)