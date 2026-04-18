"""设置窗口 - GUI 配置面板

提供图形化界面用于修改应用配置，包括：
- OCR 识别参数
- 翻译服务选择和 API 密钥
- 快捷键设置
- 显示效果调整
- 性能参数配置
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import ConfigManager


class SettingsWindow:
    """设置窗口类

    使用 Tkinter 创建配置编辑界面，支持实时预览和保存配置。
    """

    def __init__(self, parent=None):
        """初始化设置窗口

        Args:
            parent: 父窗口（可选），如果为 None 则创建独立窗口
        """
        self.config = ConfigManager()
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Control+OCR 设置")
        self.window.geometry("600x700")
        self.window.resizable(True, True)

        # 防止窗口关闭时退出整个应用
        if parent is None:
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # 创建选项卡
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个配置标签页
        self._create_ocr_tab()
        self._create_translate_tab()
        self._create_hotkey_tab()
        self._create_display_tab()
        self._create_performance_tab()

        # 底部按钮
        self._create_buttons()

        # 加载当前配置到 UI
        self._load_config_to_ui()

    def _create_ocr_tab(self):
        """创建 OCR 配置标签页"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="OCR 识别")

        # 识别半径
        ttk.Label(frame, text="识别半径 (像素):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.capture_radius_var = tk.IntVar(value=60)
        radius_spinbox = ttk.Spinbox(
            frame,
            from_=20,
            to=200,
            textvariable=self.capture_radius_var,
            width=10
        )
        radius_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="鼠标周围识别区域的半径大小",
            foreground="gray"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # 最大重试次数
        ttk.Label(frame, text="最大重试次数:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.max_retries_var = tk.IntVar(value=2)
        retries_spinbox = ttk.Spinbox(
            frame,
            from_=0,
            to=5,
            textvariable=self.max_retries_var,
            width=10
        )
        retries_spinbox.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="识别失败时的重试次数",
            foreground="gray"
        ).grid(row=1, column=2, sticky=tk.W, padx=5)

        frame.columnconfigure(2, weight=1)

    def _create_translate_tab(self):
        """创建翻译配置标签页"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="翻译服务")

        # 翻译引擎选择
        ttk.Label(frame, text="翻译引擎:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.translate_api_var = tk.StringVar(value="google")
        api_combo = ttk.Combobox(
            frame,
            textvariable=self.translate_api_var,
            values=["google", "deepl", "youdao"],
            state="readonly",
            width=15
        )
        api_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        api_combo.bind("<<ComboboxSelected>>", self._on_api_changed)
        ttk.Label(
            frame,
            text="选择翻译服务提供商",
            foreground="gray"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # 源语言
        ttk.Label(frame, text="源语言:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.source_lang_var = tk.StringVar(value="auto")
        source_combo = ttk.Combobox(
            frame,
            textvariable=self.source_lang_var,
            values=["auto", "en", "zh-CN", "ja", "ko", "fr", "de", "es"],
            state="readonly",
            width=15
        )
        source_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="自动检测或指定语言",
            foreground="gray"
        ).grid(row=1, column=2, sticky=tk.W, padx=5)

        # 目标语言
        ttk.Label(frame, text="目标语言:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.target_lang_var = tk.StringVar(value="zh-CN")
        target_combo = ttk.Combobox(
            frame,
            textvariable=self.target_lang_var,
            values=["zh-CN", "en", "ja", "ko", "fr", "de", "es"],
            state="readonly",
            width=15
        )
        target_combo.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="翻译结果的语言",
            foreground="gray"
        ).grid(row=2, column=2, sticky=tk.W, padx=5)

        # DeepL API Key
        ttk.Label(frame, text="DeepL API Key:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.deepl_api_key_var = tk.StringVar(value="")
        deepl_entry = ttk.Entry(
            frame,
            textvariable=self.deepl_api_key_var,
            width=40,
            show="*"
        )
        deepl_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)

        # 有道 App Key
        ttk.Label(frame, text="有道 App Key:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.youdao_app_key_var = tk.StringVar(value="")
        youdao_key_entry = ttk.Entry(
            frame,
            textvariable=self.youdao_app_key_var,
            width=40,
            show="*"
        )
        youdao_key_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)

        # 有道 App Secret
        ttk.Label(frame, text="有道 App Secret:").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        self.youdao_app_secret_var = tk.StringVar(value="")
        youdao_secret_entry = ttk.Entry(
            frame,
            textvariable=self.youdao_app_secret_var,
            width=40,
            show="*"
        )
        youdao_secret_entry.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)

        frame.columnconfigure(2, weight=1)

    def _create_hotkey_tab(self):
        """创建快捷键配置标签页"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="快捷键")

        # 触发键选择
        ttk.Label(frame, text="触发按键:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.trigger_var = tk.StringVar(value="ctrl")
        trigger_combo = ttk.Combobox(
            frame,
            textvariable=self.trigger_var,
            values=["ctrl", "cmd", "alt"],
            state="readonly",
            width=15
        )
        trigger_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="按住此键触发 OCR 翻译",
            foreground="gray"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # 说明文本
        info_text = (
            "使用说明:\n\n"
            "• Ctrl: 按住 Control 键触发\n"
            "• Cmd: 按住 Command 键触发 (macOS)\n"
            "• Alt: 按住 Option/Alt 键触发\n\n"
            "修改后需要重启应用生效。"
        )
        info_label = ttk.Label(
            frame,
            text=info_text,
            justify=tk.LEFT,
            foreground="#666666"
        )
        info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=20)

        frame.columnconfigure(2, weight=1)

    def _create_display_tab(self):
        """创建显示配置标签页"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="显示效果")

        # 字体大小
        ttk.Label(frame, text="字体大小:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.font_size_var = tk.IntVar(value=13)
        font_spinbox = ttk.Spinbox(
            frame,
            from_=8,
            to=32,
            textvariable=self.font_size_var,
            width=10
        )
        font_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="翻译结果的字体大小",
            foreground="gray"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # 显示时长
        ttk.Label(frame, text="显示时长 (秒):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.timeout_var = tk.IntVar(value=3)
        timeout_spinbox = ttk.Spinbox(
            frame,
            from_=1,
            to=30,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="翻译结果自动消失的时间",
            foreground="gray"
        ).grid(row=1, column=2, sticky=tk.W, padx=5)

        frame.columnconfigure(2, weight=1)

    def _create_performance_tab(self):
        """创建性能配置标签页"""
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="性能优化")

        # 防抖时间
        ttk.Label(frame, text="防抖时间 (毫秒):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.debounce_ms_var = tk.IntVar(value=600)
        debounce_spinbox = ttk.Spinbox(
            frame,
            from_=100,
            to=2000,
            increment=100,
            textvariable=self.debounce_ms_var,
            width=10
        )
        debounce_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="连续触发的最小间隔时间",
            foreground="gray"
        ).grid(row=0, column=2, sticky=tk.W, padx=5)

        # 检查间隔
        ttk.Label(frame, text="检查间隔 (秒):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.check_interval_var = tk.DoubleVar(value=0.08)
        interval_spinbox = ttk.Spinbox(
            frame,
            from_=0.01,
            to=0.5,
            increment=0.01,
            textvariable=self.check_interval_var,
            width=10,
            format="%.2f"
        )
        interval_spinbox.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="按键状态检查频率",
            foreground="gray"
        ).grid(row=1, column=2, sticky=tk.W, padx=5)

        # 缓存大小
        ttk.Label(frame, text="缓存条目数:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.cache_size_var = tk.IntVar(value=100)
        cache_spinbox = ttk.Spinbox(
            frame,
            from_=10,
            to=1000,
            textvariable=self.cache_size_var,
            width=10
        )
        cache_spinbox.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="最多缓存的翻译结果数量",
            foreground="gray"
        ).grid(row=2, column=2, sticky=tk.W, padx=5)

        # 缓存 TTL
        ttk.Label(frame, text="缓存有效期 (秒):").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.cache_ttl_var = tk.IntVar(value=3600)
        ttl_spinbox = ttk.Spinbox(
            frame,
            from_=60,
            to=86400,
            increment=60,
            textvariable=self.cache_ttl_var,
            width=10
        )
        ttl_spinbox.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Label(
            frame,
            text="缓存结果的过期时间",
            foreground="gray"
        ).grid(row=3, column=2, sticky=tk.W, padx=5)

        frame.columnconfigure(2, weight=1)

    def _create_buttons(self):
        """创建底部按钮"""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # 重置按钮
        reset_btn = ttk.Button(
            button_frame,
            text="恢复默认",
            command=self._reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame,
            text="取消",
            command=self._on_close
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # 保存按钮
        save_btn = ttk.Button(
            button_frame,
            text="保存",
            command=self._save_config
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

    def _load_config_to_ui(self):
        """从配置管理器加载配置到 UI"""
        try:
            # OCR 配置
            self.capture_radius_var.set(self.config.ocr.capture_radius)
            self.max_retries_var.set(self.config.ocr.max_retries)

            # 翻译配置
            self.translate_api_var.set(self.config.translate.api)
            self.source_lang_var.set(self.config.translate.source_lang)
            self.target_lang_var.set(self.config.translate.target_lang)
            self.deepl_api_key_var.set(self.config.translate.deepl_api_key)
            self.youdao_app_key_var.set(self.config.translate.youdao_app_key)
            self.youdao_app_secret_var.set(self.config.translate.youdao_app_secret)

            # 快捷键配置
            self.trigger_var.set(self.config.hotkey.trigger)

            # 显示配置
            self.font_size_var.set(self.config.display.font_size)
            self.timeout_var.set(self.config.display.timeout)

            # 性能配置
            self.debounce_ms_var.set(self.config.performance.debounce_ms)
            self.check_interval_var.set(self.config.performance.check_interval)
            self.cache_size_var.set(self.config.performance.cache_size)
            self.cache_ttl_var.set(self.config.performance.cache_ttl)

        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")

    def _save_config(self):
        """保存配置"""
        try:
            # 更新 OCR 配置
            self.config.ocr.capture_radius = self.capture_radius_var.get()
            self.config.ocr.max_retries = self.max_retries_var.get()

            # 更新翻译配置
            self.config.translate.api = self.translate_api_var.get()
            self.config.translate.source_lang = self.source_lang_var.get()
            self.config.translate.target_lang = self.target_lang_var.get()
            self.config.translate.deepl_api_key = self.deepl_api_key_var.get()
            self.config.translate.youdao_app_key = self.youdao_app_key_var.get()
            self.config.translate.youdao_app_secret = self.youdao_app_secret_var.get()

            # 更新快捷键配置
            self.config.hotkey.trigger = self.trigger_var.get()

            # 更新显示配置
            self.config.display.font_size = self.font_size_var.get()
            self.config.display.timeout = self.timeout_var.get()

            # 更新性能配置
            self.config.performance.debounce_ms = self.debounce_ms_var.get()
            self.config.performance.check_interval = self.check_interval_var.get()
            self.config.performance.cache_size = self.cache_size_var.get()
            self.config.performance.cache_ttl = self.cache_ttl_var.get()

            # 保存到文件
            self.config.save()

            messagebox.showinfo("成功", "配置已保存！\n部分设置可能需要重启应用后生效。")
            self._on_close()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def _reset_to_defaults(self):
        """恢复默认配置"""
        if messagebox.askyesno("确认", "确定要恢复所有设置为默认值吗？"):
            # 重新创建配置管理器以获取默认值
            default_config = ConfigManager.__new__(ConfigManager)
            default_config._initialized = False
            default_config.__init__()

            # 更新 UI
            self.capture_radius_var.set(default_config.ocr.capture_radius)
            self.max_retries_var.set(default_config.ocr.max_retries)
            self.translate_api_var.set(default_config.translate.api)
            self.source_lang_var.set(default_config.translate.source_lang)
            self.target_lang_var.set(default_config.translate.target_lang)
            self.deepl_api_key_var.set(default_config.translate.deepl_api_key)
            self.youdao_app_key_var.set(default_config.translate.youdao_app_key)
            self.youdao_app_secret_var.set(default_config.translate.youdao_app_secret)
            self.trigger_var.set(default_config.hotkey.trigger)
            self.font_size_var.set(default_config.display.font_size)
            self.timeout_var.set(default_config.display.timeout)
            self.debounce_ms_var.set(default_config.performance.debounce_ms)
            self.check_interval_var.set(default_config.performance.check_interval)
            self.cache_size_var.set(default_config.performance.cache_size)
            self.cache_ttl_var.set(default_config.performance.cache_ttl)

            messagebox.showinfo("提示", "已恢复默认值，点击保存以应用。")

    def _on_api_changed(self, event=None):
        """翻译引擎改变时的回调"""
        api = self.translate_api_var.get()
        # 可以在这里添加动态显示/隐藏 API Key 输入框的逻辑
        pass

    def _on_close(self):
        """关闭窗口"""
        self.window.destroy()

    def show(self):
        """显示设置窗口"""
        self.window.mainloop()


def open_settings(parent=None):
    """便捷函数：打开设置窗口

    Args:
        parent: 父窗口（可选）

    Returns:
        SettingsWindow 实例
    """
    settings = SettingsWindow(parent)
    return settings


if __name__ == "__main__":
    # 独立运行测试
    app = SettingsWindow()
    app.show()
