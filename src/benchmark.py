#!/usr/bin/env python3
"""快速性能基准测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from capture import capture_region, get_mouse_position
from translate import translate


def benchmark_capture():
    """测试截图性能"""
    print("\n📸 截图性能测试")
    print("-" * 40)
    
    x, y = get_mouse_position()
    print(f"鼠标位置: ({x}, {y})\n")
    
    for radius in [20, 30, 50]:
        times = []
        for _ in range(3):
            start = time.time()
            img = capture_region(x, y, radius)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg = sum(times) / len(times)
        size_kb = len(img) / 1024 if img else 0
        print(f"半径 {radius:2d}px: 平均 {avg:.3f}s, 大小 {size_kb:.1f}KB")


def benchmark_translation():
    """测试翻译性能（含缓存）"""
    print("\n🌐 翻译性能测试")
    print("-" * 40)
    
    test_word = "computer"
    
    # 首次翻译（无缓存）
    start = time.time()
    result1 = translate(test_word, use_cache=True)
    first_time = time.time() - start
    
    # 缓存翻译
    start = time.time()
    result2 = translate(test_word, use_cache=True)
    cached_time = time.time() - start
    
    print(f"测试单词: '{test_word}'")
    print(f"首次翻译: {first_time*1000:.0f}ms → {result1}")
    print(f"缓存翻译: {cached_time*1000:.0f}ms → {result2}")
    
    if first_time > 0:
        speedup = first_time / max(cached_time, 0.0001)
        print(f"加速比: {speedup:.0f}x ⚡")


def main():
    print("=" * 50)
    print("🎯 Control+OCR 性能基准测试")
    print("=" * 50)
    
    try:
        benchmark_capture()
        benchmark_translation()
        
        print("\n" + "=" * 50)
        print("✅ 测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
