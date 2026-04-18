"""结构化日志系统

提供统一的日志入口，替代所有 print() 语句。
支持控制台和文件双输出，便于调试和问题定位。
"""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "ctrl_ocr",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """配置并返回 logger 实例

    Args:
        name: logger 名称
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_file: 可选的日志文件路径

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 格式化：时间 | 级别 | 消息
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 可选文件 handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"[警告] 无法创建日志文件 {log_file}: {e}", file=sys.stderr)

    return logger


# 全局 logger 实例（延迟初始化）
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """获取全局 logger，如果未初始化则自动创建"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
