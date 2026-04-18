#!/usr/bin/env python3
"""Control+OCR 翻译器 - 优化版本

功能：按住 Control 键即可 OCR 识别鼠标位置的单词并显示翻译

优化点：
1. 减小 OCR 识别区域（30px 半径）提升速度
2. 添加翻译缓存避免重复请求
3. 悬浮窗复用减少创建开销
4. 智能文本提取只识别单词
5. 降低主循环频率减少 CPU 占用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import time
from AppKit import NSEvent
from Foundation import NSRunLoop, NSDate

# 导入优化后的模块
from capture import ocr_at_mouse, get_mouse_position
from translate import translate, clear_cache
from overlay import TranslationOverlay


class Config:
    """配置管理"""
    
    def __init__(self):
        self.radius = 60  # OCR 截图半径（像素）
        self.max_retries = 2  # OCR 重试次数
        self.target_lang = "zh-CN"  # 目标语言
        self.timeout = 3  # 悬浮窗显示时间（秒）
        self.debounce_ms = 600  # 防抖时间（毫秒）
        self.check_interval = 0.08  # 主循环检查间隔（秒）
        
        self.load_config()
    
    def load_config(self):
        """从配置文件加载设置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "config.yaml"
        )
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                
                self.radius = cfg.get("ocr", {}).get("capture_radius", 60)
                self.max_retries = cfg.get("ocr", {}).get("max_retries", 2)
                self.target_lang = cfg.get("translate", {}).get("target_lang", "zh-CN")
                self.timeout = cfg.get("display", {}).get("timeout", 3)
                
                hotkey = cfg.get("hotkey", {}).get("trigger", "ctrl")
                if hotkey == "cmd":
                    self.modifier_mask = 0x100000  # NSCommandKeyMask
                elif hotkey == "alt":
                    self.modifier_mask = 0x80000  # NSAlternateKeyMask
                else:
                    self.modifier_mask = 0x40000  # NSControlKeyMask
                    
        except Exception as e:
            print(f"[警告] 配置文件读取失败: {e}，使用默认配置")


class OCRTranslator:
    """OCR 翻译器主类"""
    
    def __init__(self):
        self.config = Config()
        self.overlay = TranslationOverlay()
        self.last_trigger_time = 0
        self.last_ocr_text = ""
        self.running = False
    
    def is_modifier_pressed(self) -> bool:
        """检查修饰键是否按下"""
        mods = NSEvent.modifierFlags()
        return bool(mods & self.config.modifier_mask)
    
    def do_translate(self):
        """执行 OCR 和翻译"""
        now = time.time() * 1000
        
        # 防抖检查
        if now - self.last_trigger_time < self.config.debounce_ms:
            return
        
        self.last_trigger_time = now
        
        try:
            # OCR 识别（传递半径和重试次数）
            word = ocr_at_mouse(self.config.radius, self.config.max_retries)
            
            if not word:
                print("[调试] 未识别到文本", flush=True)
                return
            
            # 如果和上次识别的文本相同，跳过（避免重复处理）
            if word == self.last_ocr_text:
                print(f"[调试] 跳过重复文本: {word}", flush=True)
                return
            
            self.last_ocr_text = word
            
            # 翻译
            translated = translate(word, self.config.target_lang)
            
            if translated:
                # 打印识别结果和翻译
                print(f"\n📝 识别: {word}")
                print(f"🌐 翻译: {translated}\n", flush=True)
                
                # 获取鼠标位置用于显示悬浮窗
                x, y = get_mouse_position()
                
                # 显示悬浮窗
                self.overlay.show(
                    word, 
                    translated, 
                    x, 
                    y, 
                    timeout=self.config.timeout
                )
                
        except Exception as e:
            print(f"[错误] 翻译失败: {e}", flush=True)
    
    def run(self):
        """运行主循环"""
        self.running = True
        modifier_was_pressed = False
        
        print("=" * 50, flush=True)
        print("🎯 Control+OCR 翻译器已启动", flush=True)
        print(f"⌨️  按住 {'Control' if self.config.modifier_mask == 0x40000 else 'Command' if self.config.modifier_mask == 0x100000 else 'Option'} 键翻译鼠标位置的单词", flush=True)
        print(f"⚙️  配置: 识别半径={self.config.radius}px, 显示时长={self.config.timeout}s", flush=True)
        print("🚫 按 Ctrl+C 退出", flush=True)
        print("=" * 50, flush=True)
        
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
                    NSDate.dateWithTimeIntervalSinceNow_(self.config.check_interval)
                )
                
        except KeyboardInterrupt:
            print("\n\n[信息] 正在退出...", flush=True)
            self.stop()
    
    def stop(self):
        """停止程序"""
        self.running = False
        self.overlay.cleanup()
        clear_cache()
        print("[信息] 程序已退出", flush=True)


def main():
    """主入口"""
    translator = OCRTranslator()
    translator.run()


if __name__ == "__main__":
    main()
