"""悬浮窗显示模块 - 轻量级优化版本"""
from AppKit import (
    NSWindow, NSTextField, NSColor, NSFont,
    NSMakeRect, NSTitledWindowMask, NSFloatingWindowLevel,
    NSBackingStoreBuffered, NSApp
)
from Foundation import NSTimer
import time


class TranslationOverlay:
    """翻译结果悬浮窗 - 单例模式，复用窗口实例"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.window = None
        self.text_field = None
        self.close_timer = None
        self._initialized = True
    
    def show(self, original: str, translated: str, x: int, y: int, timeout: int = 3):
        """在指定位置显示翻译结果
        
        Args:
            original: 原文
            translated: 译文
            x: 鼠标 X 坐标
            y: 鼠标 Y 坐标
            timeout: 自动关闭时间（秒）
        """
        import Quartz
        
        # 隐藏旧窗口
        self.hide()
        
        # 计算窗口位置（鼠标右下方）
        # x, y 是 macOS 屏幕坐标系（原点在左下角）
        win_x = x + 15  # 鼠标右侧 15px
        win_y = y - 50  # 鼠标下方 50px（考虑窗口高度）
        
        # 根据文本长度动态调整窗口大小
        text_content = f"{original}\n{translated}"
        line_count = text_content.count('\n') + 1
        max_line_len = max(len(line) for line in text_content.split('\n'))
        
        # 估算窗口尺寸
        width = min(max(200, max_line_len * 10), 400)
        height = min(max(60, line_count * 25), 200)
        
        # 创建或复用窗口
        if self.window is None:
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(win_x, win_y, width, height),
                NSTitledWindowMask,
                NSBackingStoreBuffered,
                False
            )
            
            self.window.setTitle_("")
            self.window.setLevel_(NSFloatingWindowLevel)
            self.window.setOpaque_(False)
            self.window.setHasShadow_(True)
            # 黑色半透明背景
            self.window.setBackgroundColor_(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1, 0.1, 0.1, 0.95)
            )
            
            # 创建文本框（复用）
            self.text_field = NSTextField.alloc().initWithFrame_(
                NSMakeRect(10, 10, width - 20, height - 20)
            )
            self.text_field.setBezeled_(False)
            self.text_field.setDrawsBackground_(False)
            self.text_field.setEditable_(False)
            self.text_field.setFont_(NSFont.systemFontOfSize_(13))
            self.text_field.setSelectable_(True)
            # 白色文字
            self.text_field.setTextColor_(NSColor.whiteColor())
            
            self.window.contentView().addSubview_(self.text_field)
        else:
            # 更新窗口位置和大小
            self.window.setFrame_display_(
                NSMakeRect(win_x, win_y, width, height),
                True
            )
        
        # 设置文本
        self.text_field.setStringValue_(text_content)
        
        # 显示窗口
        self.window.makeKeyAndOrderFront_(None)
        
        # 设置自动关闭定时器
        if timeout > 0:
            # 创建一个辅助对象来处理定时器回调
            class TimerTarget:
                def __init__(self, overlay_instance):
                    self.overlay = overlay_instance
                
                def hide_(self, timer):
                    self.overlay._do_hide()
            
            timer_target = TimerTarget(self)
            self.close_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                timeout,
                timer_target,
                "hide:",
                None,
                False
            )
    
    def _do_hide(self):
        """内部隐藏方法，供定时器调用"""
        self.hide()
    
    def hide(self):
        """隐藏窗口"""
        if self.close_timer:
            self.close_timer.invalidate()
            self.close_timer = None
        
        if self.window:
            self.window.orderOut_(None)
    
    def cleanup(self):
        """清理资源"""
        self.hide()
        if self.window:
            self.window.close()
            self.window = None
            self.text_field = None


# 全局单例
overlay = TranslationOverlay()


if __name__ == "__main__":
    import time
    
    ov = TranslationOverlay()
    ov.show("Hello", "你好", 500, 500, timeout=2)
    print("窗口显示 2 秒...")
    time.sleep(3)
    
    ov.show("World", "世界", 600, 600, timeout=2)
    print("新窗口显示 2 秒...")
    time.sleep(3)
    
    ov.cleanup()
    print("完成")
