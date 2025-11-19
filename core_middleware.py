"""
Core Middleware for LangGraph Agent

精简的中间件实现，提供核心功能：
- 日志记录
- Token 预算控制
- 安全过滤
"""

from datetime import datetime
from typing import Any
import re


class LoggingMiddleware:
    """
    日志中间件 - 记录所有消息和响应
    用于调试和监控
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.call_count = 0

    def before_invoke(self, messages: list) -> list:
        """在调用模型前记录日志"""
        self.call_count += 1

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"[MIDDLEWARE LOG] Call #{self.call_count}")
            print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[MESSAGES] {len(messages)} message(s)")
            for i, msg in enumerate(messages[-3:]):  # 只显示最后3条
                role = getattr(msg, 'type', 'unknown')
                content = str(msg.content)[:100]
                print(f"  [{role}] {content}...")
            print(f"{'='*60}")

        return messages

    def after_invoke(self, response: Any) -> Any:
        """在模型返回后记录日志"""
        if self.verbose:
            content = str(response.content)[:150] if hasattr(response, 'content') else str(response)[:150]
            print(f"\n[RESPONSE] {content}...")
            print(f"{'='*60}\n")

        return response


class TokenBudgetMiddleware:
    """
    Token 预算中间件 - 控制 API 使用成本
    防止超出预算
    """

    def __init__(self, max_tokens: int = 50000, max_requests: int = 100):
        self.max_tokens = max_tokens
        self.max_requests = max_requests
        self.total_tokens = 0
        self.request_count = 0

    def before_invoke(self, messages: list) -> list:
        """检查预算"""
        self.request_count += 1

        # 估算 token 数量（粗略估计：4字符 = 1 token）
        estimated_tokens = sum(len(str(msg.content)) for msg in messages) // 4

        print(f"\n[BUDGET] Request #{self.request_count}/{self.max_requests}")
        print(f"[BUDGET] Estimated tokens: {estimated_tokens}")
        print(f"[BUDGET] Used: {self.total_tokens}/{self.max_tokens} tokens")

        if self.total_tokens + estimated_tokens > self.max_tokens:
            raise Exception(f"Token budget exceeded! Used: {self.total_tokens}, Limit: {self.max_tokens}")

        if self.request_count > self.max_requests:
            raise Exception(f"Request limit exceeded! Limit: {self.max_requests}")

        self.total_tokens += estimated_tokens
        return messages

    def get_usage_stats(self) -> dict:
        """获取使用统计"""
        return {
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'request_count': self.request_count,
            'max_requests': self.max_requests,
            'tokens_remaining': self.max_tokens - self.total_tokens,
            'requests_remaining': self.max_requests - self.request_count
        }


class SecurityFilterMiddleware:
    """
    安全过滤中间件 - 过滤敏感信息
    防止 PII（个人身份信息）泄露
    """

    def __init__(self):
        self.redaction_count = 0
        # 敏感信息正则表达式
        self.patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3,4}[-.]?\d{4}\b'),
            'api_key': re.compile(r'\b(sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        }

    def before_invoke(self, messages: list) -> list:
        """过滤敏感信息"""
        filtered_messages = []
        redacted_this_call = False

        for msg in messages:
            content = msg.content
            original_content = content

            # 应用所有过滤规则
            for data_type, pattern in self.patterns.items():
                matches = pattern.findall(content)
                if matches:
                    content = pattern.sub(f'[REDACTED_{data_type.upper()}]', content)
                    redacted_this_call = True
                    self.redaction_count += len(matches)

            # 创建新消息对象（保留原始类型）
            if content != original_content:
                from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
                msg_type = type(msg)
                filtered_msg = msg_type(content=content)
                filtered_messages.append(filtered_msg)
            else:
                filtered_messages.append(msg)

        if redacted_this_call:
            print(f"\n[SECURITY] Redacted {self.redaction_count} sensitive item(s)")

        return filtered_messages


class MiddlewareChain:
    """
    中间件链 - 管理多个中间件的执行顺序
    """

    def __init__(self, middlewares: list = None):
        self.middlewares = middlewares or []

    def add_middleware(self, middleware):
        """添加中间件"""
        self.middlewares.append(middleware)

    def before_invoke(self, messages: list) -> list:
        """依次执行所有中间件的 before_invoke"""
        for mw in self.middlewares:
            if hasattr(mw, 'before_invoke'):
                messages = mw.before_invoke(messages)
        return messages

    def after_invoke(self, response: Any) -> Any:
        """逆序执行所有中间件的 after_invoke"""
        for mw in reversed(self.middlewares):
            if hasattr(mw, 'after_invoke'):
                response = mw.after_invoke(response)
        return response
