"""翻译服务工厂

根据配置动态创建翻译引擎实例。
使用工厂模式，支持插件式扩展新的翻译后端。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Type
from .translator import BaseTranslator
from .google_translator import GoogleTranslator
from config_manager import ConfigManager


class TranslatorFactory:
    """翻译服务工厂
    
    根据配置中的 api 字段动态创建对应的翻译引擎实例。
    支持实例缓存，避免重复创建。
    
    Usage:
        config = ConfigManager()
        translator = TranslatorFactory.create(config.translate.api, config)
    """
    
    # 注册的翻译引擎映射表
    _registry: Dict[str, Type[BaseTranslator]] = {
        'google': GoogleTranslator,
        # 未来可扩展：
        # 'deepl': DeepLTranslator,
        # 'youdao': YoudaoTranslator,
    }
    
    # 实例缓存，避免重复创建
    _instances: Dict[str, BaseTranslator] = {}
    
    @classmethod
    def register(cls, name: str, translator_class: Type[BaseTranslator]):
        """注册新的翻译引擎
        
        Args:
            name: 引擎名称（与 config.yaml 中的 api 字段对应）
            translator_class: 翻译引擎类（必须继承 BaseTranslator）
        
        Example:
            TranslatorFactory.register('deepl', DeepLTranslator)
        """
        cls._registry[name] = translator_class
        # 清除缓存，下次创建时会使用新注册的类
        cls._instances.clear()
    
    @classmethod
    def create(cls, engine_name: str, config: ConfigManager) -> BaseTranslator:
        """创建翻译引擎实例
        
        Args:
            engine_name: 引擎名称（如 'google', 'deepl'）
            config: 配置管理器实例
        
        Returns:
            翻译引擎实例
        
        Raises:
            ValueError: 如果引擎名称未注册
        
        Example:
            translator = TranslatorFactory.create('google', config)
        """
        # 检查缓存
        if engine_name in cls._instances:
            return cls._instances[engine_name]
        
        # 查找注册的引擎类
        translator_class = cls._registry.get(engine_name)
        if not translator_class:
            available = ', '.join(cls._registry.keys())
            raise ValueError(
                f"未知的翻译引擎: {engine_name}。可用的引擎: {available}"
            )
        
        # 根据引擎类型传入相应参数
        if engine_name == 'deepl':
            instance = translator_class(api_key=config.translate.deepl_api_key)
        elif engine_name == 'youdao':
            instance = translator_class(
                app_key=config.translate.youdao_app_key,
                app_secret=config.translate.youdao_app_secret
            )
        else:
            # Google 等无需参数的引擎
            instance = translator_class()
        
        # 缓存实例
        cls._instances[engine_name] = instance
        return instance
    
    @classmethod
    def get_available_engines(cls) -> list:
        """获取所有可用的翻译引擎列表
        
        Returns:
            引擎名称列表，如 ['google', 'deepl']
        """
        return list(cls._registry.keys())
    
    @classmethod
    def clear_cache(cls):
        """清空实例缓存
        
        用于测试或强制重新创建实例的场景。
        """
        cls._instances.clear()
