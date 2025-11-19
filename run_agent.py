#!/usr/bin/env python3
"""
运行 QA Agent

简单的启动脚本，支持：
- 交互式聊天
- 单次问答
- Phoenix 追踪监控
"""

import sys
from qa_agent import QAAgent
from phoenix_tracer import init_phoenix, stop_phoenix


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  LangGraph QA Agent with Middleware & Phoenix Tracing")
    print("="*70)

    # 初始化 Phoenix 追踪
    phoenix = init_phoenix()

    if phoenix.is_enabled():
        print(f"\n📊 Phoenix Dashboard: {phoenix.get_dashboard_url()}")
        print("   Open this URL in your browser to view real-time traces\n")

    # 创建 Agent
    try:
        agent = QAAgent(
            model_provider="deepseek",
            enable_logging=True,
            enable_budget=True,
            enable_security=True,
            max_tokens=100000,
            max_requests=200
        )
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {str(e)}")
        print("   Please check your .env file and ensure DEEPSEEK_API_KEY is set\n")
        stop_phoenix()
        sys.exit(1)

    # 检查命令行参数
    if len(sys.argv) > 1:
        # 单次问答模式
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}\n")
        try:
            answer = agent.ask(question)
            print(f"Answer: {answer}\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
    else:
        # 交互式聊天模式
        try:
            agent.chat()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")

    # 清理 Phoenix
    stop_phoenix()


def demo_examples():
    """运行一些演示示例"""
    print("\n" + "="*70)
    print("  Demo Examples - QA Agent in Action")
    print("="*70 + "\n")

    # 初始化 Phoenix
    phoenix = init_phoenix()

    if phoenix.is_enabled():
        print(f"📊 Phoenix Dashboard: {phoenix.get_dashboard_url()}\n")

    # 创建 Agent
    agent = QAAgent(
        model_provider="deepseek",
        enable_logging=True,
        enable_budget=True,
        enable_security=True
    )

    # 示例 1: 简单问答
    print("\n" + "="*70)
    print("Example 1: Simple QA")
    print("="*70)
    q1 = "What is LangGraph?"
    print(f"\nQ: {q1}")
    a1 = agent.ask(q1, thread_id="demo1")
    print(f"\nA: {a1}\n")

    # 示例 2: 多轮对话
    print("\n" + "="*70)
    print("Example 2: Multi-turn Conversation")
    print("="*70)

    questions = [
        "My name is Alice",
        "What's my name?",
        "Tell me a joke about programming"
    ]

    for i, q in enumerate(questions, 1):
        print(f"\nQ{i}: {q}")
        a = agent.ask(q, thread_id="demo2")
        print(f"A{i}: {a}")

    # 示例 3: 安全过滤测试
    print("\n" + "="*70)
    print("Example 3: Security Filter (PII Protection)")
    print("="*70)
    q3 = "My email is test@example.com and phone is 123-456-7890. Can you help?"
    print(f"\nQ: {q3}")
    print("(Note: Email and phone will be redacted by security middleware)")
    a3 = agent.ask(q3, thread_id="demo3")
    print(f"\nA: {a3}\n")

    # 显示使用统计
    if hasattr(agent, 'budget_mw'):
        print("\n" + "="*70)
        print("Usage Statistics")
        print("="*70)
        stats = agent.budget_mw.get_usage_stats()
        print(f"\n📊 Token Usage: {stats['total_tokens']}/{stats['max_tokens']}")
        print(f"📊 Requests: {stats['request_count']}/{stats['max_requests']}")
        print(f"📊 Remaining: {stats['tokens_remaining']} tokens, {stats['requests_remaining']} requests\n")

    # 清理
    stop_phoenix()


if __name__ == "__main__":
    # 检查是否运行 demo
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_examples()
    else:
        main()
