import os
import sys
import time
import zipfile

from loguru import logger

logger.add(sys.stdout, colorize=True)
logger.add('file_{time}.log')

# 配置代码目录和输出压缩包路径
CODE_DIR = r"c:\code"
OUTPUT_ZIP = r"c:\temp\code_package.zip"
EXCLUDE_FILE = "exclude_patterns.txt"


def load_exclude_patterns(file_path):
    """从配置文件加载排除规则"""
    if not os.path.exists(file_path):
        logger.warning(f'no exclude_patterns.txt file found. path: {file_path} not exists.')
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def should_exclude(file_path, exclude_patterns):
    """根据排除规则判断是否排除文件或目录"""
    for pattern in exclude_patterns:
        if pattern in file_path:
            return True
    return False


def create_zip(source_dir, output_zip, exclude_patterns):
    """创建压缩包，排除指定的文件和目录"""
    # zipfile.ZIP_DEFLATED Elapsed time: 148.57 seconds
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_LZMA) as zf:
        for root, dirs, files in os.walk(source_dir):
            # 过滤需要排除的目录
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
            for file in files:
                file_path = os.path.join(root, file)
                if not should_exclude(file_path, exclude_patterns):
                    arcname = os.path.relpath(file_path, start=source_dir)
                    zf.write(file_path, arcname)
                    logger.debug(f"Added: {arcname}")


def main():
    start_time = time.time()  # 开始计时

    exclude_patterns = load_exclude_patterns(EXCLUDE_FILE)
    logger.info(f"Excluding patterns: {exclude_patterns}")

    os.makedirs(os.path.dirname(OUTPUT_ZIP), exist_ok=True)
    logger.info(f"Output zip file: {OUTPUT_ZIP}")

    create_zip(CODE_DIR, OUTPUT_ZIP, exclude_patterns)
    logger.info(f"Packaging complete. File saved to: {OUTPUT_ZIP}")

    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
