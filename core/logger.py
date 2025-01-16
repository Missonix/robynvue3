import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    :param name: 日志记录器名称
    :param log_level: 日志级别
    :return: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 如果日志记录器已经有处理器，直接返回
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 创建文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        filename=log_dir / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式化器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 