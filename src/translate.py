"""翻译模块 - 兼容层（已废弃，请使用 services 模块）

此模块保留用于向后兼容，内部调用新的架构。
新代码应直接使用 services.translator 和 services.factory。
"""
import warnings
from config_manager import ConfigManager
from services.factory import TranslatorFactory
from services.cached_translator import CachedTranslator

warnings.warn(
    "translate 模块已废弃，请使用 services.translator",
    DeprecationWarning,
    stacklevel=2
)

# 全局实例（懒加载）
_translator = None


def _get_translator():
    """获取或创建翻译服务实例"""
    global _translator
    if _translator is None:
        config = ConfigManager()
        base = TranslatorFactory.create(config.translate.api, config)
        _translator = CachedTranslator(base, config)
    return _translator


def translate(text: str, target_lang: str = "zh-CN", use_cache: bool = True) -> str:
    """兼容旧接口的翻译函数
    
    Args:
        text: 要翻译的文本
        target_lang: 目标语言
        use_cache: 是否使用缓存（保留参数，实际始终使用缓存）
    
    Returns:
        翻译结果字符串
    """
    translator = _get_translator()
    result = translator.translate(text, target_lang)
    return result.translated_text if result.success else f"[错误: {result.error_message}]"


def clear_cache():
    """清空缓存"""
    _get_translator().clear_cache()


if __name__ == "__main__":
    import time
    
    # 测试翻译（应该看到 DeprecationWarning）
    print("测试翻译功能...")
    
    start = time.time()
    result1 = translate("Hello, world!")
    elapsed1 = time.time() - start
    print(f"EN→ZH: {result1} (耗时: {elapsed1:.2f}s)")
    
    # 测试缓存（应该更快）
    start = time.time()
    result2 = translate("Hello, world!")
    elapsed2 = time.time() - start
    print(f"EN→ZH (缓存): {result2} (耗时: {elapsed2:.2f}s)")
    
    result3 = translate("你好世界", "en")
    print(f"ZH→EN: {result3}")
