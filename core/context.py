# core/context.py
from contextvars import ContextVar
from typing import Optional, Dict

# 定义线程安全的上下文变量
current_user: ContextVar[Optional[Dict]] = ContextVar("current_user", default=None)

def get_current_user() -> Optional[Dict]:
    return current_user.get()

def set_current_user(user_info: Dict):
    current_user.set(user_info)