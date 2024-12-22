import os
import sys
import time
import zipfile

from loguru import logger
from pathspec import PathSpec

logger.add(sys.stdout, colorize=True)
logger.add('file_{time}.log')

# 配置代码目录和输出压缩包路径
CODE_DIR = r"c:\code"
OUTPUT_ZIP = r"c:\temp\code_ssd.zip"
GLOBAL_EXCLUDE_FILE = "exclude_patterns.txt"


def load_pathspec(file_path):
    """加载一个文件中的路径匹配规则（支持 .gitignore 语法）"""
    if not os.path.exists(file_path):
        return PathSpec.from_lines('gitwildmatch', [])
    with open(file_path, 'r', encoding='utf-8') as f:
        return PathSpec.from_lines('gitwildmatch', f)


def load_gitignore_patterns(dir_path):
    """加载当前目录下的 .gitignore 文件规则"""
    gitignore_path = os.path.join(dir_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        return None
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        return PathSpec.from_lines('gitwildmatch', f)


def should_exclude(file_path, global_pathspec, local_pathspec=None):
    """判断是否应该排除文件或目录"""
    relative_path = os.path.relpath(file_path, start=CODE_DIR)
    # 全局规则
    if global_pathspec.match_file(relative_path):
        return True
    # 局部规则 (.gitignore)
    if local_pathspec and local_pathspec.match_file(relative_path):
        return True
    return False


def create_zip(source_dir, output_zip, global_pathspec):
    """创建压缩包，排除指定的文件和目录"""
    # zipfile.ZIP_DEFLATED: Elapsed time: 148.57 seconds, Size 2,243,121,526 bytes
    # zipfile.ZIP_LZMA: Elapsed time: 1390.17 seconds, Size 1,853,347,560 bytes
    # zipfile.ZIP_BZIP2: Elapsed time: 311.60 seconds, Size 2,134,891,733 bytes
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # 加载当前目录的 .gitignore 规则
            gitignore_spec = load_gitignore_patterns(root)

            # 过滤需要排除的目录
            dirs[:] = [
                d for d in dirs
                if not should_exclude(os.path.join(root, d), global_pathspec, gitignore_spec)
            ]

            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path, global_pathspec, gitignore_spec):
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zf.write(file_path, arcname)
                    logger.debug(f"Added: {arcname}")


def main():
    start_time = time.time()  # 开始计时

    # 加载全局排除规则
    global_pathspec = load_pathspec(GLOBAL_EXCLUDE_FILE)
    logger.info(f"Loaded global exclusion patterns: {global_pathspec}")

    os.makedirs(os.path.dirname(OUTPUT_ZIP), exist_ok=True)
    logger.info(f"Output zip file: {OUTPUT_ZIP}")

    create_zip(CODE_DIR, OUTPUT_ZIP, global_pathspec)
    logger.info(f"Packaging complete. File saved to: {OUTPUT_ZIP}")

    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
