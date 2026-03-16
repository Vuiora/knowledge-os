"""
配置管理器
负责加载、验证和管理系统配置
"""

import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from .models import Config
from .logger import logger


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigManager:
    """配置管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'scan': {
            'root_dir': 'knowledge',
            'excluded_dirs': [
                'javascripts',
                'stylesheets',
                '_site',
                '_wiki',
                'templates',
                '.git',
                '__pycache__'
            ]
        },
        'templates': {
            'main_layer': 'templates/main_layer.md',
            'sub_topic': 'templates/sub_topic.md',
            'difficulty': 'templates/difficulty.md',
            'content': 'templates/content.md'
        },
        'generation': {
            'force_overwrite': False,
            'create_backup': True,
            'dry_run': False
        },
        'logging': {
            'level': 'INFO',
            'file': ''
        }
    }
    
    def __init__(self):
        """初始化配置管理器"""
        self._config_data: Dict[str, Any] = {}
        self._config: Optional[Config] = None
    
    def load_config(self, path: Optional[str] = None) -> Config:
        """
        加载配置文件
        
        Args:
            path: 配置文件路径（可选）
            
        Returns:
            Config: 配置对象
            
        Raises:
            ConfigValidationError: 配置验证失败
        """
        if path is None:
            logger.info("未指定配置文件，使用默认配置")
            self._config_data = self.DEFAULT_CONFIG.copy()
        else:
            config_path = Path(path)
            
            if not config_path.exists():
                logger.warning(f"配置文件不存在: {path}，使用默认配置")
                self._config_data = self.DEFAULT_CONFIG.copy()
            else:
                try:
                    self._config_data = self._load_file(config_path)
                    logger.info(f"成功加载配置文件: {path}")
                except Exception as e:
                    logger.error(f"加载配置文件失败: {path}", e)
                    logger.warning("使用默认配置")
                    self._config_data = self.DEFAULT_CONFIG.copy()
        
        # 合并默认配置（确保所有必需字段都存在）
        self._config_data = self._merge_with_defaults(self._config_data)
        
        # 验证配置
        self.validate_config()
        
        # 转换为 Config 对象
        self._config = self._to_config_object()
        
        return self._config
    
    def _load_file(self, path: Path) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Args:
            path: 配置文件路径
            
        Returns:
            Dict: 配置字典
            
        Raises:
            ValueError: 不支持的文件格式
            yaml.YAMLError: YAML 解析错误
            json.JSONDecodeError: JSON 解析错误
        """
        suffix = path.suffix.lower()
        
        with open(path, 'r', encoding='utf-8') as f:
            if suffix in ['.yml', '.yaml']:
                return yaml.safe_load(f) or {}
            elif suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {suffix}，仅支持 .yml, .yaml, .json")
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将用户配置与默认配置合并
        
        Args:
            config: 用户配置
            
        Returns:
            Dict: 合并后的配置
        """
        import copy
        merged = copy.deepcopy(self.DEFAULT_CONFIG)
        
        # 深度合并
        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        
        return merged
    
    def validate_config(self) -> None:
        """
        验证配置的正确性
        
        Raises:
            ConfigValidationError: 配置验证失败
        """
        errors = []
        
        # 验证 scan 部分
        if 'scan' not in self._config_data:
            errors.append("缺少 'scan' 配置节")
        else:
            scan = self._config_data['scan']
            
            if 'root_dir' not in scan:
                errors.append("缺少 'scan.root_dir' 配置项")
            elif not isinstance(scan['root_dir'], str):
                errors.append("'scan.root_dir' 必须是字符串类型")
            
            if 'excluded_dirs' in scan and not isinstance(scan['excluded_dirs'], list):
                errors.append("'scan.excluded_dirs' 必须是列表类型")
        
        # 验证 templates 部分
        if 'templates' not in self._config_data:
            errors.append("缺少 'templates' 配置节")
        else:
            templates = self._config_data['templates']
            
            if not isinstance(templates, dict):
                errors.append("'templates' 必须是字典类型")
            else:
                required_templates = ['main_layer', 'sub_topic', 'difficulty', 'content']
                for template_type in required_templates:
                    if template_type not in templates:
                        logger.warning(f"缺少模板配置: {template_type}，将使用默认值")
                        templates[template_type] = self.DEFAULT_CONFIG['templates'][template_type]
                    elif not isinstance(templates[template_type], str):
                        errors.append(f"'templates.{template_type}' 必须是字符串类型")
        
        # 验证 generation 部分
        if 'generation' in self._config_data:
            generation = self._config_data['generation']
            
            if not isinstance(generation, dict):
                errors.append("'generation' 必须是字典类型")
            else:
                if 'force_overwrite' in generation and not isinstance(generation['force_overwrite'], bool):
                    errors.append("'generation.force_overwrite' 必须是布尔类型")
                
                if 'create_backup' in generation and not isinstance(generation['create_backup'], bool):
                    errors.append("'generation.create_backup' 必须是布尔类型")
                
                if 'dry_run' in generation and not isinstance(generation['dry_run'], bool):
                    errors.append("'generation.dry_run' 必须是布尔类型")
        
        # 验证 logging 部分
        if 'logging' in self._config_data:
            logging_config = self._config_data['logging']
            
            if not isinstance(logging_config, dict):
                errors.append("'logging' 必须是字典类型")
            else:
                if 'level' in logging_config:
                    level = logging_config['level']
                    if not isinstance(level, str):
                        errors.append("'logging.level' 必须是字符串类型")
                    elif level.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                        errors.append(f"'logging.level' 值无效: {level}，必须是 DEBUG, INFO, WARNING, ERROR 之一")
                
                if 'file' in logging_config and not isinstance(logging_config['file'], str):
                    errors.append("'logging.file' 必须是字符串类型")
        
        if errors:
            error_message = "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_message)
            raise ConfigValidationError(error_message)
        
        logger.debug("配置验证通过")
    
    def _to_config_object(self) -> Config:
        """
        将配置字典转换为 Config 对象
        
        Returns:
            Config: 配置对象
        """
        scan = self._config_data['scan']
        templates = self._config_data['templates']
        generation = self._config_data['generation']
        logging_config = self._config_data['logging']
        
        return Config(
            root_dir=scan['root_dir'],
            excluded_dirs=scan.get('excluded_dirs', []),
            template_paths=templates,
            force_overwrite=generation.get('force_overwrite', False),
            create_backup=generation.get('create_backup', True),
            dry_run=generation.get('dry_run', False),
            log_level=logging_config.get('level', 'INFO'),
            log_file=logging_config.get('file', '')
        )
    
    def get_config(self) -> Optional[Config]:
        """
        获取当前配置对象
        
        Returns:
            Optional[Config]: 配置对象，如果未加载则返回 None
        """
        return self._config
    
    def get_excluded_dirs(self) -> List[str]:
        """
        获取排除目录列表
        
        Returns:
            List[str]: 排除目录列表
        """
        if self._config:
            return self._config.excluded_dirs
        return self.DEFAULT_CONFIG['scan']['excluded_dirs']
    
    def get_template_path(self, template_type: str) -> str:
        """
        获取指定类型的模板路径
        
        Args:
            template_type: 模板类型 (main_layer, sub_topic, difficulty, content)
            
        Returns:
            str: 模板路径
        """
        if self._config:
            return self._config.template_paths.get(
                template_type,
                self.DEFAULT_CONFIG['templates'].get(template_type, '')
            )
        return self.DEFAULT_CONFIG['templates'].get(template_type, '')
