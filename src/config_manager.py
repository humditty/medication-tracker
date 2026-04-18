"""配置管理器

统一管理配置加载、验证、保存。
使用 dataclass 定义类型安全的配置结构，支持运行时重新加载。
"""
import os
import yaml
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class OcrConfig:
    """OCR 配置"""
    capture_radius: int = 60
    max_retries: int = 2


@dataclass
class TranslateConfig:
    """翻译配置"""
    source_lang: str = "auto"
    target_lang: str = "zh-CN"
    api: str = "google"  # google | deepl | youdao
    deepl_api_key: str = ""
    youdao_app_key: str = ""
    youdao_app_secret: str = ""


@dataclass
class HotkeyConfig:
    """快捷键配置"""
    trigger: str = "ctrl"  # ctrl | cmd | alt


@dataclass
class DisplayConfig:
    """显示配置"""
    font_size: int = 13
    timeout: int = 3


@dataclass
class PerformanceConfig:
    """性能配置"""
    debounce_ms: int = 600
    check_interval: float = 0.08
    cache_size: int = 100
    cache_ttl: int = 3600


class ConfigManager:
    """配置管理器 - 单例模式

    从 config.yaml 加载所有配置项，提供类型安全的属性访问。
    支持运行时重新加载和保存配置。
    """

    _instance: Optional['ConfigManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.ocr = OcrConfig()
        self.translate = TranslateConfig()
        self.hotkey = HotkeyConfig()
        self.display = DisplayConfig()
        self.performance = PerformanceConfig()

        self._config_path = self._find_config_file()
        self.load()
        self._initialized = True

    def _find_config_file(self) -> str:
        """查找配置文件路径

        优先级：
        1. 环境变量 CTRL_OCR_CONFIG 指定的路径
        2. 项目根目录的 config.yaml
        """
        # 优先使用环境变量指定的路径
        env_path = os.environ.get('CTRL_OCR_CONFIG')
        if env_path and os.path.exists(env_path):
            return env_path

        # 默认在项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_path = os.path.join(project_root, "config.yaml")

        if os.path.exists(config_path):
            return config_path

        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    def load(self):
        """从 YAML 文件加载配置"""
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)

            if not cfg:
                return

            # 更新 OCR 配置
            if 'ocr' in cfg:
                for key, value in cfg['ocr'].items():
                    if hasattr(self.ocr, key):
                        setattr(self.ocr, key, value)

            # 更新翻译配置
            if 'translate' in cfg:
                for key, value in cfg['translate'].items():
                    if hasattr(self.translate, key):
                        setattr(self.translate, key, value)

            # 更新快捷键配置
            if 'hotkey' in cfg:
                for key, value in cfg['hotkey'].items():
                    if hasattr(self.hotkey, key):
                        setattr(self.hotkey, key, value)

            # 更新显示配置
            if 'display' in cfg:
                for key, value in cfg['display'].items():
                    if hasattr(self.display, key):
                        setattr(self.display, key, value)

            # 更新性能配置（之前未被使用的配置段）
            if 'performance' in cfg:
                for key, value in cfg['performance'].items():
                    if hasattr(self.performance, key):
                        setattr(self.performance, key, value)

        except Exception as e:
            from logger import get_logger
            get_logger().error(f"配置加载失败: {e}，使用默认值")

    def reload(self):
        """重新加载配置（用于设置面板修改后）"""
        self.load()

    def save(self):
        """保存当前配置到 YAML 文件"""
        cfg = {
            'ocr': {
                'capture_radius': self.ocr.capture_radius,
                'max_retries': self.ocr.max_retries,
            },
            'translate': {
                'source_lang': self.translate.source_lang,
                'target_lang': self.translate.target_lang,
                'api': self.translate.api,
                'deepl_api_key': self.translate.deepl_api_key,
                'youdao_app_key': self.translate.youdao_app_key,
                'youdao_app_secret': self.translate.youdao_app_secret,
            },
            'hotkey': {
                'trigger': self.hotkey.trigger,
            },
            'display': {
                'font_size': self.display.font_size,
                'timeout': self.display.timeout,
            },
            'performance': {
                'debounce_ms': self.performance.debounce_ms,
                'check_interval': self.performance.check_interval,
                'cache_size': self.performance.cache_size,
                'cache_ttl': self.performance.cache_ttl,
            }
        }

        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            from logger import get_logger
            get_logger().error(f"配置保存失败: {e}")

    def get_modifier_mask(self) -> int:
        """根据配置获取修饰键掩码

        Returns:
            macOS NSEvent 修饰键掩码
        """
        trigger = self.hotkey.trigger
        masks = {
            'ctrl': 0x40000,   # NSControlKeyMask
            'cmd': 0x100000,   # NSCommandKeyMask
            'alt': 0x80000,    # NSAlternateKeyMask
        }
        return masks.get(trigger, 0x40000)
