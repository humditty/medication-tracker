#!/usr/bin/env python3
"""Control+OCR 翻译器 - 重构版本

功能：按住 Control 键即可 OCR 识别鼠标位置的单词并显示翻译

架构改进：
1. 使用配置管理器统一管理所有配置项
2. 使用结构化日志系统替代 print()
3. 使用工厂模式创建翻译服务，支持多引擎切换
4. 使用装饰器模式添加缓存功能
5. 依赖注入，降低模块耦合度
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from AppKit import NSEvent
from Foundation import NSRunLoop, NSDate

# 导入重构后的模块
from logger import setup_logger
from config_manager import ConfigManager
from services.factory import TranslatorFactory
from services.cached_translator import CachedTranslator
from capture import ocr_at_mouse, get_mouse_position
from overlay import TranslationOverlay


class OCRTranslator:
    """OCR 翻译器主类 - 重构版
    
    使用依赖注入和工厂模式，降低模块耦合度。
    支持运行时切换翻译引擎，配置完全生效。
    """
    
    def __init__(self):
        # 初始化日志
        log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ctrl_ocr.log"
        )
        self.logger = setup_logger(
            name="ctrl_ocr",
            log_file=log_file
        )
        
        # 加载配置（包括之前未使用的 performance 段）
        self.config = ConfigManager()
        self.logger.info(f"配置加载完成，翻译引擎: {self.config.translate.api}")
        
        # 创建带缓存的翻译服务（使用工厂模式）
        base_translator = TranslatorFactory.create(
            self.config.translate.api,
            self.config
        )
        self.translator = CachedTranslator(base_translator, self.config)
        self.logger.info(f"翻译服务初始化: {self.translator.name}")
        
        # 初始化 UI
        self.overlay = TranslationOverlay()
        
        # 状态管理
        self.last_trigger_time = 0
        self.last_ocr_text = ""
        self.running = False
        
        # 计算修饰键掩码（从配置读取）
        self.modifier_mask = self.config.get_modifier_mask()
    
    def is_modifier_pressed(self) -> bool:
        """检查修饰键是否按下"""
        mods = NSEvent.modifierFlags()
        return bool(mods & self.modifier_mask)
    
    def do_translate(self):
        """执行 OCR 和翻译"""
        now = time.time() * 1000
        
        # 防抖检查（从配置读取）
        if now - self.last_trigger_time < self.config.performance.debounce_ms:
            return
        
        self.last_trigger_time = now
        
        try:
            # OCR 识别（从配置读取半径和重试次数）
            word = ocr_at_mouse(
                self.config.ocr.capture_radius,
                self.config.ocr.max_retries
            )
            
            if not word:
                self.logger.debug("未识别到文本")
                return
            
            # 跳过重复文本
            if word == self.last_ocr_text:
                self.logger.debug(f"跳过重复文本: {word}")
                return
            
            self.last_ocr_text = word
            
            # 翻译（使用新的翻译服务）
            result = self.translator.translate(
                word,
                self.config.translate.target_lang
            )
            
            if result.success:
                self.logger.info(f"识别: {word} | 翻译: {result.translated_text}")
                
                # 获取鼠标位置用于显示悬浮窗
                x, y = get_mouse_position()
                
                # 显示悬浮窗（超时从配置读取）
                self.overlay.show(
                    word,
                    result.translated_text,
                    x,
                    y,
                    timeout=self.config.display.timeout
                )
            else:
                self.logger.warning(f"翻译失败: {result.error_message}")
                
        except Exception as e:
            self.logger.error(f"翻译流程异常: {e}", exc_info=True)
    
    def run(self):
        """运行主循环"""
        self.running = True
        modifier_was_pressed = False
        
        # 使用结构化日志输出启动信息
        trigger_name = {
            0x40000: 'CTRL',
            0x100000: 'CMD',
            0x80000: 'OPTION'
        }.get(self.modifier_mask, 'CTRL')
        
        self.logger.info("=" * 50)
        self.logger.info("🎯 Control+OCR 翻译器已启动")
        self.logger.info(f"⌨️  快捷键: {trigger_name}")
        self.logger.info(f"🌐 翻译引擎: {self.translator.name}")
        self.logger.info(f"⚙️  配置: 识别半径={self.config.ocr.capture_radius}px, "
                        f"显示时长={self.config.display.timeout}s")
        self.logger.info("🚫 按 Ctrl+C 退出")
        self.logger.info("=" * 50)
        
        try:
            while self.running:
                # 检查修饰键状态
                modifier_pressed = self.is_modifier_pressed()
                
                # 检测按键按下事件（边沿触发）
                if modifier_pressed and not modifier_was_pressed:
                    self.do_translate()
                
                modifier_was_pressed = modifier_pressed
                
                # 使用 AppKit 事件循环（必须！否则悬浮窗无法显示）
                NSRunLoop.currentRunLoop().runUntilDate_(
                    NSDate.dateWithTimeIntervalSinceNow_(
                        self.config.performance.check_interval
                    )
                )
                
        except KeyboardInterrupt:
            self.logger.info("用户中断，正在退出...")
            self.stop()
    
    def stop(self):
        """停止程序"""
        self.running = False
        self.overlay.cleanup()
        self.translator.clear_cache()
        self.logger.info("程序已退出")


def main():
    """主入口"""
    translator = OCRTranslator()
    translator.run()


if __name__ == "__main__":
    main()
