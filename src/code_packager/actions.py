import time
from loguru import logger
from .packager import CodePackager
from .utils import validate_source_directory, ensure_output_directory, print_statistics
from .config import ConfigManager

def run_packaging_task(source_dir, output_zip, preset=None, config_path=None, remove_comments=False, compression="deflate"):
    """
    执行代码打包任务
    
    Args:
        source_dir: 源代码目录
        output_zip: 输出ZIP文件路径
        preset: 预设配置名称
        config_path: 自定义配置文件路径
        remove_comments: 是否移除注释
        compression: 压缩方法
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    # 验证和准备目录
    if not validate_source_directory(source_dir):
        return False

    if not ensure_output_directory(output_zip):
        return False

    # 加载配置
    config_manager = ConfigManager()
    
    # 获取路径规则
    if config_path:
        pathspec = config_manager.load_custom_config(config_path)
    else:
        # 默认预设为 basic
        preset = preset or "basic"
        pathspec = config_manager.load_pathspec_from_preset(preset)
    
    # 创建打包器实例
    packager = CodePackager(pathspec)
    
    # 开始打包
    start_time = time.time()
    
    try:
        stats = packager.create_zip(
            source_dir, 
            output_zip,
            remove_comments=remove_comments,
            compression_method=compression
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 显示统计信息
        print_statistics(stats, elapsed_time, output_zip, remove_comments)
        return True
        
    except Exception as e:
        logger.error(f"打包过程中发生错误: {e}")
        return False
