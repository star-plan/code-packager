"""代码打包工具主入口

灵活的代码打包工具，支持多种配置方案和高级功能。
"""

import os
import time
from loguru import logger

from .cli import CommandLineInterface
from .packager import CodePackager
from .utils import setup_logger, validate_source_directory, ensure_output_directory, print_statistics





def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    # 创建CLI实例并解析参数
    cli = CommandLineInterface()
    args = cli.parse_arguments()
    
    # 如果只是列出预设方案
    if args.list_presets:
        cli.list_presets()
        return
    
    # 检查必需参数
    if not args.source_dir or not args.output_zip:
        logger.error("错误: 请提供源代码目录和输出压缩包路径")
        logger.info("使用 --help 查看帮助信息")
        return
    
    # 验证和准备目录
    source_dir = validate_source_directory(args.source_dir)
    if not source_dir:
        return
    
    output_zip = ensure_output_directory(args.output_zip)
    if not output_zip:
        return
    
    # 创建打包器实例
    packager = CodePackager(
        preset=args.preset,
        config_file=args.config,
        remove_comments=args.remove_comments,
        compression_method=args.compression,
        verbose=args.verbose
    )
    
    # 开始打包
    start_time = time.time()
    
    try:
        stats = packager.create_package(source_dir, output_zip)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 显示统计信息
        print_statistics(stats, output_zip, elapsed_time)
        
    except Exception as e:
         logger.error(f"打包过程中发生错误: {e}")
         return


if __name__ == '__main__':
    main()
