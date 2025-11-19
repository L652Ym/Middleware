"""
LangGraph QA Agent with Middleware Support

使用 LangGraph 构建的问答 Agent，集成中间件功能
"""

import os
from typing import Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

from core_middleware import MiddlewareChain, LoggingMiddleware, TokenBudgetMiddleware, SecurityFilterMiddleware

# 加载环境变量
load_dotenv()


class QAAgent:
    """
    问答 Agent - 使用 LangGraph 和中间件

    特性：
    - 支持多轮对话
    - 自动应用中间件
    - 状态持久化
    - DeepSeek 模型
    """

    def __init__(
        self,
        model_provider: str = "deepseek",
        enable_logging: bool = True,
        enable_budget: bool = True,
        enable_security: bool = True,
        max_tokens: int = 50000,
        max_requests: int = 100
    ):
        """
        初始化 QA Agent

        Args:
            model_provider: 模型提供商 ("deepseek", "openai")
            enable_logging: 启用日志中间件
            enable_budget: 启用预算控制中间件
            enable_security: 启用安全过滤中间件
            max_tokens: 最大 token 数
            max_requests: 最大请求数
        """
        # 初始化模型
        self.model = self._init_model(model_provider)

        # 初始化中间件链
        self.middleware_chain = MiddlewareChain()

        # 添加中间件
        if enable_logging:
            self.middleware_chain.add_middleware(LoggingMiddleware(verbose=True))

        if enable_budget:
            self.budget_mw = TokenBudgetMiddleware(
                max_tokens=max_tokens,
                max_requests=max_requests
            )
            self.middleware_chain.add_middleware(self.budget_mw)

        if enable_security:
            self.middleware_chain.add_middleware(SecurityFilterMiddleware())

        # 初始化检查点（用于状态持久化）
        self.checkpointer = MemorySaver()

        # 构建 LangGraph
        self.graph = self._build_graph()

        print(f"\n✓ QA Agent initialized with {len(self.middleware_chain.middlewares)} middleware(s)")

    def _init_model(self, model_provider: str):
        """初始化 LLM 模型"""
        if model_provider == "deepseek":
            model = ChatOpenAI(
                model=os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-chat"),
                temperature=0.7,
                openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
                openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            )
            print(f"✓ Using DeepSeek Chat Model")
        elif model_provider == "openai":
            model = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            print(f"✓ Using OpenAI GPT-3.5-Turbo")
        else:
            raise ValueError(f"Unknown model provider: {model_provider}")

        return model

    def _build_graph(self):
        """构建 LangGraph 状态图"""

        # 定义节点函数
        def apply_middleware_before(state: MessagesState):
            """应用中间件（调用前）"""
            messages = state["messages"]
            processed = self.middleware_chain.before_invoke(list(messages))
            return {"messages": processed}

        def call_model(state: MessagesState):
            """调用 LLM 模型"""
            messages = state["messages"]

            # 确保有系统消息
            has_system = any(isinstance(msg, SystemMessage) for msg in messages)
            if not has_system:
                system_msg = SystemMessage(content="You are a helpful AI assistant.")
                messages = [system_msg] + list(messages)

            response = self.model.invoke(messages)
            return {"messages": [response]}

        def apply_middleware_after(state: MessagesState):
            """应用中间件（调用后）"""
            messages = state["messages"]
            if messages:
                last_msg = messages[-1]
                processed = self.middleware_chain.after_invoke(last_msg)
                # 替换最后一条消息
                new_messages = list(messages[:-1]) + [processed]
                return {"messages": new_messages}
            return {"messages": messages}

        # 构建图
        graph_builder = StateGraph(MessagesState)

        # 添加节点
        graph_builder.add_node("middleware_before", apply_middleware_before)
        graph_builder.add_node("call_model", call_model)
        graph_builder.add_node("middleware_after", apply_middleware_after)

        # 设置边
        graph_builder.add_edge(START, "middleware_before")
        graph_builder.add_edge("middleware_before", "call_model")
        graph_builder.add_edge("call_model", "middleware_after")
        graph_builder.add_edge("middleware_after", END)

        # 编译图
        compiled = graph_builder.compile(checkpointer=self.checkpointer)

        return compiled

    def ask(self, question: str, thread_id: str = "default") -> str:
        """
        提问并获取回答

        Args:
            question: 用户问题
            thread_id: 对话线程 ID（用于多轮对话）

        Returns:
            Agent 的回答
        """
        # 创建用户消息
        user_message = HumanMessage(content=question)

        # 配置（用于检查点）
        config = {"configurable": {"thread_id": thread_id}}

        # 调用图
        result = self.graph.invoke(
            {"messages": [user_message]},
            config=config
        )

        # 提取最后一条消息
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return last_message.content
        return ""

    def chat(self, thread_id: str = "default"):
        """
        交互式聊天模式

        Args:
            thread_id: 对话线程 ID
        """
        print("\n" + "="*60)
        print("QA Agent - Interactive Chat Mode")
        print("="*60)
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'stats' to see usage statistics")
        print("="*60 + "\n")

        while True:
            try:
                # 获取用户输入
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # 退出命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋\n")
                    break

                # 显示统计信息
                if user_input.lower() == 'stats':
                    if hasattr(self, 'budget_mw'):
                        stats = self.budget_mw.get_usage_stats()
                        print(f"\n📊 Usage Statistics:")
                        print(f"  Tokens: {stats['total_tokens']}/{stats['max_tokens']} ({stats['tokens_remaining']} remaining)")
                        print(f"  Requests: {stats['request_count']}/{stats['max_requests']} ({stats['requests_remaining']} remaining)")
                        print()
                    continue

                # 获取回答
                response = self.ask(user_input, thread_id=thread_id)
                print(f"\nAgent: {response}\n")

            except KeyboardInterrupt:
                print("\n\nChat interrupted. Goodbye! 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                break

    def get_conversation_history(self, thread_id: str = "default") -> list:
        """
        获取对话历史

        Args:
            thread_id: 对话线程 ID

        Returns:
            消息列表
        """
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)
        return state.values.get("messages", [])
