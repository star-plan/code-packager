import os
import sys
import time
import zipfile
import argparse
import re
from pathlib import Path
from typing import Optional, Dict, List

from loguru import logger
from pathspec import PathSpec

# 移除默认的stderr处理器，避免重复输出
logger.remove()
logger.add(sys.stdout, colorize=True, level="INFO")
logger.add(os.path.join('logs', 'file_{time}.log'), level="DEBUG")

# 预设配置方案
PRESET_CONFIGS = {
    'basic': {
        'name': '基础方案',
        'description': '排除常见的构建文件和缓存，适用于大多数项目',
        'file': 'presets/basic.conf'
    },
    'git-friendly': {
        'name': 'Git友好方案',
        'description': '保留.git目录但排除大文件，适用于需要版本控制信息的场景',
        'file': 'presets/git-friendly.conf'
    },
    'complete': {
        'name': '完整方案',
        'description': '排除所有不必要文件包括.git，适用于最终发布',
        'file': 'presets/complete.conf'
    },
    'lightweight': {
        'name': '轻量级方案',
        'description': '只保留核心源代码，适用于代码审查和学习',
        'file': 'presets/lightweight.conf'
    },
    'custom': {
        'name': '自定义方案',
        'description': '使用exclude_patterns.conf文件',
        'file': 'exclude_patterns.conf'
    }
}


def load_pathspec_from_file(file_path: str) -> PathSpec:
    """从文件加载路径匹配规则（支持 .gitignore 语法）"""
    if not os.path.exists(file_path):
        logger.warning(f"配置文件不存在: {file_path}")
        return PathSpec.from_lines('gitwildmatch', [])
    with open(file_path, 'r', encoding='utf-8') as f:
        return PathSpec.from_lines('gitwildmatch', f)


def load_pathspec_from_preset(preset_name: str) -> PathSpec:
    """从预设方案加载路径匹配规则"""
    if preset_name not in PRESET_CONFIGS:
        logger.error(f"未知的预设方案: {preset_name}")
        return PathSpec.from_lines('gitwildmatch', [])
    
    config = PRESET_CONFIGS[preset_name]
    if 'file' in config:
        # 构建配置文件的完整路径
        config_file = config['file']
        if not os.path.isabs(config_file):
            # 相对于当前脚本目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(script_dir, config_file)
        return load_pathspec_from_file(config_file)
    elif 'patterns' in config:
        return PathSpec.from_lines('gitwildmatch', config['patterns'])
    else:
        return PathSpec.from_lines('gitwildmatch', [])


def _is_docstring_start(lines: List[str], line_index: int) -> bool:
    """检查指定行是否是docstring的开始"""
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


def remove_comments_from_content(content: str, file_extension: str) -> str:
    """根据文件类型去除代码注释和文档字符串"""
    if file_extension in ['.py']:
        # Python注释和docstring处理
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
            if _is_docstring_start(lines, i):
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
    
    elif file_extension in ['.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h']:
        # JavaScript/TypeScript/Java/C/C++注释处理
        # 简单实现，去除//和/* */注释
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    return content


def load_gitignore_patterns(dir_path):
    """加载当前目录下的 .gitignore 文件规则"""
    gitignore_path = os.path.join(dir_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        return None
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        return PathSpec.from_lines('gitwildmatch', f)


def should_exclude(file_path: str, source_dir: str, global_pathspec: PathSpec, local_pathspec: Optional[PathSpec] = None) -> bool:
    """判断是否应该排除文件或目录"""
    relative_path = os.path.relpath(file_path, start=source_dir)
    # 全局规则
    if global_pathspec.match_file(relative_path):
        return True
    # 局部规则 (.gitignore)
    if local_pathspec and local_pathspec.match_file(relative_path):
        return True
    return False


def create_zip(source_dir: str, output_zip: str, global_pathspec: PathSpec, 
               remove_comments: bool = False, compression_method: int = zipfile.ZIP_DEFLATED) -> Dict[str, any]:
    """创建压缩包，排除指定的文件和目录"""
    stats = {
        'total_files': 0,
        'included_files': 0,
        'excluded_files': 0,
        'total_size': 0,
        'compressed_size': 0,
        'files_with_comments_removed': 0
    }
    
    logger.info(f"开始打包: {source_dir} -> {output_zip}")
    logger.info(f"压缩方法: {compression_method}")
    logger.info(f"去除注释: {'是' if remove_comments else '否'}")
    
    with zipfile.ZipFile(output_zip, 'w', compression_method, allowZip64=True) as zf:
        for root, dirs, files in os.walk(source_dir):
            # 加载当前目录的 .gitignore 规则
            gitignore_spec = load_gitignore_patterns(root)

            # 过滤需要排除的目录
            dirs[:] = [
                d for d in dirs
                if not should_exclude(os.path.join(root, d), source_dir, global_pathspec, gitignore_spec)
            ]

            for file in files:
                file_path = os.path.join(root, file)
                stats['total_files'] += 1
                
                if not should_exclude(file_path, source_dir, global_pathspec, gitignore_spec):
                    arcname = os.path.relpath(file_path, start=source_dir)
                    
                    # 获取文件大小
                    file_size = os.path.getsize(file_path)
                    stats['total_size'] += file_size
                    
                    if remove_comments:
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h']:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                processed_content = remove_comments_from_content(content, file_ext)
                                if processed_content != content:
                                    stats['files_with_comments_removed'] += 1
                                    # 将处理后的内容写入压缩包
                                    zf.writestr(arcname, processed_content.encode('utf-8'))
                                else:
                                    zf.write(file_path, arcname)
                            except (UnicodeDecodeError, Exception) as e:
                                logger.warning(f"无法处理文件 {file_path}: {e}，使用原文件")
                                zf.write(file_path, arcname)
                        else:
                            zf.write(file_path, arcname)
                    else:
                        zf.write(file_path, arcname)
                    
                    stats['included_files'] += 1
                    logger.debug(f"已添加: {arcname} ({file_size} bytes)")
                else:
                    stats['excluded_files'] += 1
                    logger.debug(f"已排除: {os.path.relpath(file_path, start=source_dir)}")
    
    # 获取压缩后大小
    stats['compressed_size'] = os.path.getsize(output_zip)
    return stats


def format_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def list_presets():
    """列出所有可用的预设方案"""
    print("\n可用的预设方案:")
    print("=" * 50)
    for key, config in PRESET_CONFIGS.items():
        print(f"  {key:12} - {config['name']}")
        print(f"               {config['description']}")
        print()


def parse_arguments():
    """解析命令行参数"""
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
    
    parser.add_argument('source_dir', nargs='?', help='要打包的源代码目录')
    parser.add_argument('output_zip', nargs='?', help='输出的压缩包路径')
    
    parser.add_argument('--preset', '-p', choices=list(PRESET_CONFIGS.keys()),
                       default='basic', help='使用预设配置方案 (默认: basic)')
    
    parser.add_argument('--config', '-c', help='使用自定义配置文件')
    
    parser.add_argument('--remove-comments', '-r', action='store_true',
                       help='去除代码注释 (支持 Python, JavaScript, Java, C/C++)')
    
    parser.add_argument('--compression', choices=['deflate', 'lzma', 'bzip2'],
                       default='deflate', help='压缩方法 (默认: deflate)')
    
    parser.add_argument('--list-presets', '-l', action='store_true',
                       help='列出所有可用的预设方案')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细输出')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 如果只是列出预设方案
    if args.list_presets:
        list_presets()
        return
    
    # 检查必需参数
    if not args.source_dir or not args.output_zip:
        print("错误: 请提供源代码目录和输出压缩包路径")
        print("使用 --help 查看帮助信息")
        return
    
    # 设置日志级别
    if args.verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG", colorize=True)
        logger.add(os.path.join('logs', 'file_{time}.log'), level="DEBUG")
    
    source_dir = os.path.abspath(args.source_dir)
    output_zip = os.path.abspath(args.output_zip)
    
    # 验证源目录
    if not os.path.exists(source_dir):
        logger.error(f"源目录不存在: {source_dir}")
        return
    
    if not os.path.isdir(source_dir):
        logger.error(f"源路径不是目录: {source_dir}")
        return
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_zip), exist_ok=True)
    
    # 加载配置
    if args.config:
        logger.info(f"使用自定义配置文件: {args.config}")
        global_pathspec = load_pathspec_from_file(args.config)
    else:
        logger.info(f"使用预设方案: {args.preset} ({PRESET_CONFIGS[args.preset]['name']})")
        global_pathspec = load_pathspec_from_preset(args.preset)
    
    # 设置压缩方法
    compression_map = {
        'deflate': zipfile.ZIP_DEFLATED,
        'lzma': zipfile.ZIP_LZMA,
        'bzip2': zipfile.ZIP_BZIP2
    }
    compression_method = compression_map[args.compression]
    
    # 开始打包
    start_time = time.time()
    
    try:
        stats = create_zip(
            source_dir=source_dir,
            output_zip=output_zip,
            global_pathspec=global_pathspec,
            remove_comments=args.remove_comments,
            compression_method=compression_method
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 显示统计信息
        logger.info("\n" + "=" * 60)
        logger.info("打包完成! 统计信息:")
        logger.info("=" * 60)
        logger.info(f"总文件数量:     {stats['total_files']:,}")
        logger.info(f"包含文件数量:   {stats['included_files']:,}")
        logger.info(f"排除文件数量:   {stats['excluded_files']:,}")
        logger.info(f"原始总大小:     {format_size(stats['total_size'])}")
        logger.info(f"压缩后大小:     {format_size(stats['compressed_size'])}")
        
        if stats['total_size'] > 0:
            compression_ratio = (1 - stats['compressed_size'] / stats['total_size']) * 100
            logger.info(f"压缩率:         {compression_ratio:.1f}%")
        
        if args.remove_comments and stats['files_with_comments_removed'] > 0:
            logger.info(f"去除注释文件:   {stats['files_with_comments_removed']}")
        
        logger.info(f"处理时间:       {elapsed_time:.2f} 秒")
        logger.info(f"输出文件:       {output_zip}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"打包过程中发生错误: {e}")
        raise


if __name__ == "__main__":
    main()
