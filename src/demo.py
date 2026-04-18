#!/usr/bin/env python3
"""
演示程序 - 模拟完整的 OCR + 翻译 + 弹窗流程
将鼠标移动到英文单词上，然后运行此脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from capture import ocr_at_mouse, get_mouse_position
from translate import translate
from overlay import TranslationOverlay
from Foundation import NSRunLoop, NSDate
import time


def demo():
    """演示完整流程"""
    print("=" * 70)
    print("🎯 Control+OCR 翻译器 - 演示程序")
    print("=" * 70)
    print("\n使用说明:")
    print("1. 将鼠标移动到屏幕上的英文单词上")
    print("2. 按 Enter 键开始识别和翻译")
    print("3. 翻译结果会显示在悬浮窗中")
    print("4. 输入 'q' 退出程序")
    print("=" * 70)
    
    overlay = TranslationOverlay()
    
    try:
        while True:
            # 等待用户输入
            user_input = input("\n按 Enter 开始识别（输入 q 退出）: ")
            
            if user_input.lower() == 'q':
                break
            
            print("\n📸 正在识别...")
            
            # 1. OCR 识别
            word = ocr_at_mouse(radius=30)
            
            if not word:
                print("❌ 未能识别到文本，请重试")
                continue
            
            print(f"✅ 识别结果: {word}")
            
            # 2. 翻译
            print("🌐 正在翻译...")
            translated = translate(word, "zh-CN")
            print(f"✅ 翻译结果: {translated}")
            
            # 3. 获取鼠标位置
            x, y = get_mouse_position()
            
            # 4. 显示悬浮窗
            print(f"🪟 显示悬浮窗（位置: {x}, {y}）")
            overlay.show(word, translated, x, y, timeout=5)
            
            # 运行事件循环让悬浮窗显示
            print("⏳ 悬浮窗将显示 5 秒...")
            end_time = time.time() + 5
            while time.time() < end_time:
                NSRunLoop.currentRunLoop().runUntilDate_(
                    NSDate.dateWithTimeIntervalSinceNow_(0.1)
                )
            
            print("✅ 完成！")
    
    except KeyboardInterrupt:
        print("\n\n[信息] 程序已退出")
    finally:
        overlay.cleanup()
        print("\n👋 再见！")


if __name__ == "__main__":
    demo()
