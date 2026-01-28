"""代码打包工具主入口

灵活的代码打包工具，支持多种配置方案和高级功能。
支持 TUI (终端用户界面) 和 CLI (命令行界面) 两种模式。
"""

import sys
from .utils import setup_logger

def run_tui():
    """运行 TUI 模式"""
    from .tui import CodePackagerApp
    app = CodePackagerApp()
    app.run()

def run_cli():
    """运行 CLI 模式"""
    from .cli import CommandLineInterface
    from .actions import run_packaging_task
    from loguru import logger
    
    # 设置 CLI 日志
    setup_logger()
    
    cli = CommandLineInterface()
    args = cli.parse_arguments()
    
    # 如果只是列出预设方案
    if args.list_presets:
        cli.list_presets()
        return
    
    # 检查必需参数
    # 注意: argparse 通常会在 parse_arguments 阶段处理 --help 并退出
    # 如果到了这里，说明没有 --help，但可能缺少必需参数
    if not args.source_dir or not args.output_zip:
        logger.error("错误: 请提供源代码目录和输出压缩包路径")
        logger.info("使用 --help 查看帮助信息")
        # 也可以在这里选择进入 TUI，但通常 explicit CLI args implies CLI mode
        return

    run_packaging_task(
        source_dir=args.source_dir,
        output_zip=args.output_zip,
        preset=args.preset,
        config_path=args.config,
        remove_comments=args.remove_comments,
        compression=args.compression
    )

def main():
    """主函数"""
    # 如果有命令行参数，进入 CLI 模式
    if len(sys.argv) > 1:
        run_cli()
    else:
        # 否则进入 TUI 模式
        run_tui()

if __name__ == '__main__':
    main()
