"""键盘监听模块"""
from pynput import keyboard
from typing import Callable
import time


class HotKeyListener:
    """全局热键监听器"""
    
    def __init__(
        self,
        on_trigger: Callable[[], None],
        trigger_key: str = "ctrl"
    ):
        self.on_trigger = on_trigger
        self.trigger_key = trigger_key
        
        self.key_map = {
            "ctrl": keyboard.Key.ctrl,
            "cmd": keyboard.Key.cmd,
            "alt": keyboard.Key.alt,
        }
        
        self.last_trigger = 0
        self.debounce_ms = 500
        self.key_pressed = False
        self.listener = None
    
    def _on_press(self, key):
        target = self.key_map.get(self.trigger_key)
        if key == target and not self.key_pressed:
            self.key_pressed = True
            now = time.time() * 1000
            if now - self.last_trigger > self.debounce_ms:
                self.last_trigger = now
                try:
                    self.on_trigger()
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def _on_release(self, key):
        target = self.key_map.get(self.trigger_key)
        if key == target:
            self.key_pressed = False
    
    def start(self):
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop(self):
        if self.listener:
            self.listener.stop()


if __name__ == "__main__":
    def on_ctrl():
        print(f"[{time.strftime('%H:%M:%S')}] Control pressed!")
    
    listener = HotKeyListener(on_ctrl, "ctrl")
    listener.start()
    
    print("Listening for Control key... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
        print("\nStopped.")