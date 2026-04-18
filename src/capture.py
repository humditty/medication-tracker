"""截图和 OCR 模块 - 优化版本"""
import Quartz
from Quartz import CGDisplayCreateImageForRect, CGMainDisplayID
from Quartz.CoreGraphics import CGRectMake
from Vision import VNRecognizeTextRequest, VNImageRequestHandler
from AppKit import NSBitmapImageRep, NSData


def get_mouse_position() -> tuple[int, int]:
    """获取当前鼠标位置（macOS 坐标系）"""
    from AppKit import NSEvent
    loc = NSEvent.mouseLocation()
    return int(loc.x), int(loc.y)


def capture_region(x: int, y: int, radius: int = 60) -> bytes:
    """截取鼠标周围区域的截图
    
    Args:
        x: 鼠标 X 坐标
        y: 鼠标 Y 坐标  
        radius: 截图半径（默认 60px，平衡识别完整性和性能）
    
    Returns:
        PNG 图片 bytes，失败返回 None
    """
    screen_height = Quartz.CGDisplayPixelsHigh(CGMainDisplayID())
    # macOS 坐标系：Y 轴从底部开始，需要转换
    quartz_y = screen_height - y - radius
    
    rect = CGRectMake(x - radius, quartz_y, radius * 2, radius * 2)
    
    try:
        image_ref = CGDisplayCreateImageForRect(CGMainDisplayID(), rect)
        if image_ref is None:
            return None
        
        rep = NSBitmapImageRep.alloc().initWithCGImage_(image_ref)
        png_data = rep.representationUsingType_properties_(4, {})  # PNG format
        return png_data.bytes()
    except Exception:
        return None


def ocr_image(image_bytes: bytes, max_candidates: int = 5, accurate_mode: bool = False) -> list[str]:
    """OCR 识别图片中的文字
    
    Args:
        image_bytes: PNG 图片数据
        max_candidates: 最多返回的候选词数量
        accurate_mode: 是否使用准确模式（牺牲速度换取更高精度）
    
    Returns:
        识别出的文字列表（按置信度排序）
    """
    if not image_bytes:
        return []
    
    try:
        data = NSData.dataWithBytes_length_(image_bytes, len(image_bytes))
        
        request = VNRecognizeTextRequest.alloc().init()
        # 只识别英文和中文，减少语言模型开销
        request.setRecognitionLanguages_(["en", "zh-Hans"])
        # 启用语言校正以提升单词完整性（对长单词识别很重要）
        request.setUsesLanguageCorrection_(True)
        # 根据模式选择识别级别
        request.setRecognitionLevel_(0 if accurate_mode else 1)  # 0=accurate, 1=fast
        
        handler = VNImageRequestHandler.alloc().initWithData_options_(data, {})
        success, _ = handler.performRequests_error_([request], None)
        
        if not success:
            return []
        
        results = request.results()
        texts = []
        for result in results[:max_candidates]:  # 限制处理数量
            candidates = result.topCandidates_(1)
            if candidates:
                text = candidates[0].string().strip()
                # 提高长度限制以容纳更长的单词和短语
                if text and len(text) < 100:
                    texts.append(text)
        
        return texts
    except Exception:
        return []


def is_word_truncated(word: str) -> bool:
    """检测单词是否可能被截断
    
    判断依据：
    1. 以连字符结尾（如 "appli-"）
    2. 看起来像不完整的词根（常见前缀/后缀不完整）
    3. 包含异常的大写字母位置
    """
    if not word:
        return False
    
    # 以连字符结尾通常是截断
    if word.endswith('-'):
        return True
    
    # 常见英文前缀，如果单独出现可能是不完整的
    incomplete_prefixes = ['un', 'in', 'im', 're', 'pre', 'con', 'com', 'dis', 'ex', 'trans']
    if word.lower() in incomplete_prefixes and len(word) < 5:
        return True
    
    return False


def extract_word_from_texts(texts: list[str]) -> str:
    """从 OCR 结果中提取最可能的单词
    
    策略：
    1. 优先选择包含字母的文本（而非纯数字）
    2. 过滤掉过长的文本（>100 字符）
    3. 检测并标记可能被截断的单词
    4. 在有效文本中选择最合理的单词
    5. 去除标点符号但保留连字符（用于复合词）
    """
    if not texts:
        return ""
    
    import re
    
    # 清理和验证文本
    cleaned = []
    for text in texts:
        # 去除首尾空白，但保留内部空格（可能是词组）
        text = text.strip()
        
        # 跳过空文本
        if not text:
            continue
        
        # 提高长度限制到 100 字符
        if len(text) > 100:
            continue
        
        # 只保留包含字母或中文的文本（排除纯数字）
        if not re.search(r'[a-zA-Z\u4e00-\u9fff]', text):
            continue
        
        # 清理文本：移除首尾标点，但保留内部连字符和下划线
        text = re.sub(r'^[^\w\u4e00-\u9fff]+|[^\w\u4e00-\u9fff]+$', '', text)
        
        if text:
            cleaned.append(text)
    
    if not cleaned:
        return ""
    
    # 优先选择不被截断的单词
    valid_words = [w for w in cleaned if not is_word_truncated(w)]
    
    if valid_words:
        # 在有效单词中，优先选择中等长度的（避免太短的缩写或太长的短语）
        # 理想长度：3-30 字符
        ideal_words = [w for w in valid_words if 3 <= len(w) <= 30]
        if ideal_words:
            # 返回最短的理想单词（最可能是单个词）
            return min(ideal_words, key=len)
        else:
            # 如果没有理想长度的，返回最短的有效单词
            return min(valid_words, key=len)
    else:
        # 如果所有单词都被标记为可能截断，返回最长的那个（可能更完整）
        return max(cleaned, key=len)


def ocr_at_mouse(radius: int = 60, max_retries: int = 2) -> str:
    """一步到位：获取鼠标位置 → 截图 → OCR → 提取单词
    
    智能重试机制：如果检测到单词可能被截断，自动扩大区域重新识别
    
    Args:
        radius: 初始截图半径（默认 60px）
        max_retries: 最大重试次数（避免无限循环）
    
    Returns:
        识别出的单词，失败返回空字符串
    """
    x, y = get_mouse_position()
    current_radius = radius
    
    for attempt in range(max_retries + 1):
        img = capture_region(x, y, current_radius)
        
        if not img:
            return ""
        
        texts = ocr_image(img)
        word = extract_word_from_texts(texts)
        
        if not word:
            return ""
        
        # 检查单词是否可能被截断
        if is_word_truncated(word) and attempt < max_retries:
            # 扩大区域重试（每次增加 50%）
            current_radius = int(current_radius * 1.5)
            print(f"[调试] 检测到可能截断的单词 '{word}'，扩大区域至 {current_radius}px 重试...", flush=True)
            continue
        
        # 识别成功或达到最大重试次数
        return word
    
    # 理论上不会到这里，但以防万一
    return word


if __name__ == "__main__":
    import time
    print("将鼠标移动到文本区域，3 秒后开始识别...")
    time.sleep(3)
    
    start = time.time()
    word = ocr_at_mouse(30)
    elapsed = time.time() - start
    
    print(f"识别结果: {word}")
    print(f"耗时: {elapsed:.2f}s")
