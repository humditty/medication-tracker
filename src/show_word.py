#!/usr/bin/env python3
"""
快速测试 - 识别并显示鼠标位置的单词
用法: python src/show_word.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from capture import ocr_at_mouse, get_mouse_position
from translate import translate
from overlay import TranslationOverlay
from Foundation import NSRunLoop, NSDate
import time


def main():
    print("🎯 将鼠标移动到要识别的单词上...")
    print("3 秒后开始识别...\n")
    time.sleep(3)
    
    # 获取鼠标位置
    x, y = get_mouse_position()
    print(f"📍 鼠标位置: ({x}, {y})")
    
    # OCR 识别
    print("📸 正在识别...")
    word = ocr_at_mouse(radius=30)
    
    if not word:
        print("❌ 识别失败，请重试")
        return
    
    print(f"✅ 识别结果: {word}")
    
    # 翻译
    print("🌐 正在翻译...")
    translated = translate(word, "zh-CN")
    print(f"✅ 翻译结果: {translated}")
    
    # 显示悬浮窗
    print(f"\n🪟 显示悬浮窗（3 秒后自动关闭）...")
    overlay = TranslationOverlay()
    overlay.show(word, translated, x, y, timeout=3)
    
    # 运行事件循环
    end_time = time.time() + 4
    while time.time() < end_time:
        NSRunLoop.currentRunLoop().runUntilDate_(
            NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )
    
    overlay.cleanup()
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
