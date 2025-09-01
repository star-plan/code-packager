"""配置管理模块

负责管理预设配置方案和路径匹配规则的加载。
"""

import os
from typing import Dict, Any
from pathspec import PathSpec
from loguru import logger


class ConfigManager:
    """配置管理类
    
    负责管理预设配置方案和路径匹配规则的加载。
    """
    
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
    
    def __init__(self):
        """初始化配置管理器"""
        self._script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def get_preset_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有预设配置方案
        
        Returns:
            Dict[str, Dict[str, Any]]: 预设配置字典
        """
        return self.PRESET_CONFIGS.copy()
    
    def get_preset_names(self) -> list:
        """获取所有预设方案名称
        
        Returns:
            list: 预设方案名称列表
        """
        return list(self.PRESET_CONFIGS.keys())
    
    def is_valid_preset(self, preset_name: str) -> bool:
        """检查预设方案是否有效
        
        Args:
            preset_name (str): 预设方案名称
            
        Returns:
            bool: 是否为有效的预设方案
        """
        return preset_name in self.PRESET_CONFIGS
    
    def load_pathspec_from_file(self, file_path: str) -> PathSpec:
        """从文件加载路径匹配规则（支持 .gitignore 语法）
        
        Args:
            file_path (str): 配置文件路径
            
        Returns:
            PathSpec: 路径匹配规则对象
        """
        if not os.path.exists(file_path):
            logger.warning(f"配置文件不存在: {file_path}")
            return PathSpec.from_lines('gitwildmatch', [])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return PathSpec.from_lines('gitwildmatch', f)
        except Exception as e:
            logger.error(f"读取配置文件失败 {file_path}: {e}")
            return PathSpec.from_lines('gitwildmatch', [])
    
    def load_pathspec_from_preset(self, preset_name: str) -> PathSpec:
        """从预设方案加载路径匹配规则
        
        Args:
            preset_name (str): 预设方案名称
            
        Returns:
            PathSpec: 路径匹配规则对象
        """
        if not self.is_valid_preset(preset_name):
            logger.error(f"未知的预设方案: {preset_name}")
            return PathSpec.from_lines('gitwildmatch', [])
        
        config = self.PRESET_CONFIGS[preset_name]
        
        if 'file' in config:
            # 构建配置文件的完整路径
            config_file = config['file']
            if not os.path.isabs(config_file):
                # 相对于当前脚本目录
                config_file = os.path.join(self._script_dir, config_file)
            return self.load_pathspec_from_file(config_file)
        elif 'patterns' in config:
            return PathSpec.from_lines('gitwildmatch', config['patterns'])
        else:
            return PathSpec.from_lines('gitwildmatch', [])
    
    def list_presets(self) -> None:
        """列出所有可用的预设方案"""
        print("\n可用的预设方案:")
        print("=" * 50)
        for key, config in self.PRESET_CONFIGS.items():
            print(f"  {key:12} - {config['name']}")
            print(f"               {config['description']}")
            print()