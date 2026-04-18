"""带缓存的翻译服务包装器

使用装饰器模式，为任意翻译引擎添加缓存功能。
缓存大小和 TTL 从配置读取，解决配置形同虚设问题。
"""
import time
from .translator import BaseTranslator, TranslationResult
from config_manager import ConfigManager


class CachedTranslator(BaseTranslator):
    """带缓存的翻译服务包装器
    
    使用装饰器模式，透明地为底层翻译引擎添加缓存功能。
    缓存策略：
    - LRU 淘汰：超出容量时删除最久未使用的条目
    - TTL 过期：超过有效期自动失效
    - 只缓存成功结果：失败请求不缓存，允许重试
    
    Usage:
        base_translator = TranslatorFactory.create('google', config)
        cached = CachedTranslator(base_translator, config)
        result = cached.translate('Hello', 'zh-CN')
    """
    
    def __init__(self, translator: BaseTranslator, config: ConfigManager):
        """初始化缓存包装器
        
        Args:
            translator: 底层翻译引擎实例
            config: 配置管理器，用于读取缓存配置
        """
        self._translator = translator
        self._cache: dict = {}
        self._max_size = config.performance.cache_size
        self._ttl = config.performance.cache_ttl
    
    @property
    def name(self) -> str:
        return f"{self._translator.name} (Cached)"
    
    def translate(
        self,
        text: str,
        target_lang: str = "zh-CN",
        source_lang: str = "auto"
    ) -> TranslationResult:
        """执行翻译（带缓存）
        
        先检查缓存，命中则直接返回；否则调用底层引擎并缓存结果。
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言代码
            source_lang: 源语言代码
        
        Returns:
            TranslationResult 对象
        """
        cache_key = f"{text}:{source_lang}:{target_lang}"
        
        # 检查缓存
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._ttl:
                return cached_result
            else:
                # 过期，删除
                del self._cache[cache_key]
        
        # 执行翻译
        result = self._translator.translate(text, target_lang, source_lang)
        
        # 只缓存成功的结果
        if result.success:
            self._add_to_cache(cache_key, result)
        
        return result
    
    def _add_to_cache(self, key: str, result: TranslationResult):
        """添加到缓存，超出容量时删除最旧的
        
        Args:
            key: 缓存键
            result: 翻译结果
        """
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self._max_size:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k][1]
            )
            del self._cache[oldest_key]
        
        self._cache[key] = (result, time.time())
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
    
    def is_available(self) -> bool:
        """检查底层服务是否可用"""
        return self._translator.is_available()
