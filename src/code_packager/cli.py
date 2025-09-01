"""命令行接口模块

负责处理命令行参数解析和用户交互。
"""

import argparse
from typing import Any

from .config import ConfigManager


class CommandLineInterface:
    """命令行接口类
    
    负责处理命令行参数解析和用户交互。
    """
    
    def __init__(self):
        """初始化命令行接口"""
        self.config_manager = ConfigManager()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器
        
        Returns:
            argparse.ArgumentParser: 参数解析器
        """
        parser = argparse.ArgumentParser(
            description='灵活的代码打包工具 - 支持多种配置方案和高级功能',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""示例用法:
%(prog)s /path/to/code output.zip --preset basic
%(prog)s /path/to/code output.zip --preset git-friendly --remove-comments
%(prog)s /path/to/code output.zip --config custom.conf --compression lzma
%(prog)s --list-presets
            """
        )
        
        # 位置参数
        parser.add_argument('source_dir', nargs='?', help='要打包的源代码目录')
        parser.add_argument('output_zip', nargs='?', help='输出的压缩包路径')
        
        # 配置选项
        parser.add_argument(
            '--preset', '-p', 
            choices=self.config_manager.get_preset_names(),
            default='basic', 
            help='使用预设配置方案 (默认: basic)'
        )
        
        parser.add_argument(
            '--config', '-c', 
            help='使用自定义配置文件'
        )
        
        # 功能选项
        parser.add_argument(
            '--remove-comments', '-r', 
            action='store_true',
            help='去除代码注释 (支持 Python, JavaScript, Java, C/C++)'
        )
        
        parser.add_argument(
            '--compression', 
            choices=['deflate', 'lzma', 'bzip2'],
            default='deflate', 
            help='压缩方法 (默认: deflate)'
        )
        
        # 信息选项
        parser.add_argument(
            '--list-presets', '-l', 
            action='store_true',
            help='列出所有可用的预设方案'
        )
        
        parser.add_argument(
            '--verbose', '-v', 
            action='store_true',
            help='显示详细输出'
        )
        
        return parser
    
    def parse_arguments(self, args=None) -> argparse.Namespace:
        """解析命令行参数
        
        Args:
            args: 命令行参数列表，None表示使用sys.argv
            
        Returns:
            argparse.Namespace: 解析后的参数
        """
        return self.parser.parse_args(args)
    
    def validate_arguments(self, args: argparse.Namespace) -> tuple[bool, str]:
        """验证命令行参数
        
        Args:
            args (argparse.Namespace): 解析后的参数
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        # 如果只是列出预设方案，不需要其他参数
        if args.list_presets:
            return True, ""
        
        # 检查必需参数
        if not args.source_dir or not args.output_zip:
            return False, "错误: 请提供源代码目录和输出压缩包路径\n使用 --help 查看帮助信息"
        
        # 验证预设方案
        if args.preset and not self.config_manager.is_valid_preset(args.preset):
            return False, f"错误: 未知的预设方案 '{args.preset}'"
        
        return True, ""
    
    def show_help(self) -> None:
        """显示帮助信息"""
        self.parser.print_help()
    
    def list_presets(self) -> None:
        """列出所有可用的预设方案"""
        self.config_manager.list_presets()
    
    def get_config_manager(self) -> ConfigManager:
        """获取配置管理器实例
        
        Returns:
            ConfigManager: 配置管理器实例
        """
        return self.config_manager