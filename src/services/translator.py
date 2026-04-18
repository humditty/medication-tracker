"""翻译服务接口定义

定义所有翻译引擎必须实现的抽象基类。
使用策略模式，支持运行时切换翻译后端。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """翻译结果
    
    Attributes:
        success: 是否成功
        original_text: 原始文本
        translated_text: 翻译后的文本（成功时）
        error_message: 错误信息（失败时）
        engine_name: 使用的翻译引擎名称
    """
    success: bool
    original_text: str
    translated_text: str = ""
    error_message: str = ""
    engine_name: str = ""


class BaseTranslator(ABC):
    """翻译服务基类
    
    所有翻译引擎必须继承此类并实现抽象方法。
    使用策略模式，允许运行时切换不同的翻译后端。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """翻译引擎名称
        
        Returns:
            引擎的显示名称，如 "Google Translate"、"DeepL"
        """
        pass
    
    @abstractmethod
    def translate(
        self,
        text: str,
        target_lang: str = "zh-CN",
        source_lang: str = "auto"
    ) -> TranslationResult:
        """执行翻译
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码（如 zh-CN, en, ja）
            source_lang: 源语言代码（默认 auto 自动检测）
        
        Returns:
            TranslationResult 对象，包含翻译结果和状态
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用
        
        用于验证 API Key 是否配置、网络连接是否正常等。
        
        Returns:
            True 如果服务可用，False 否则
        """
        pass
