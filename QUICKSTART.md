# 🚀 Quick Start Guide

精简版 LangGraph QA Agent，集成中间件和 Phoenix 追踪。

## 📦 安装

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd Middleware

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY
```

## ⚙️ 配置

编辑 `.env` 文件：

```env
# DeepSeek API（必填）
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat

# Phoenix 追踪（可选）
PHOENIX_ENABLED=true
PHOENIX_HOST=http://localhost
PHOENIX_PORT=6006
```

## 🎯 使用方法

### 方法 1: 交互式聊天

```bash
python run_agent.py
```

启动后可以直接输入问题：
```
You: What is LangGraph?
Agent: LangGraph is a framework for building...

You: Tell me more
Agent: ...

You: stats  # 查看使用统计
You: quit   # 退出
```

### 方法 2: 单次问答

```bash
python run_agent.py "What is machine learning?"
```

### 方法 3: 运行演示示例

```bash
python run_agent.py --demo
```

将运行 3 个示例：
1. 简单问答
2. 多轮对话
3. 安全过滤测试

## 🔧 代码使用

```python
from qa_agent import QAAgent
from phoenix_tracer import init_phoenix

# 初始化 Phoenix（可选）
phoenix = init_phoenix()

# 创建 Agent
agent = QAAgent(
    model_provider="deepseek",
    enable_logging=True,      # 启用日志
    enable_budget=True,       # 启用预算控制
    enable_security=True,     # 启用安全过滤
    max_tokens=100000,        # 最大 token 数
    max_requests=200          # 最大请求数
)

# 单次问答
answer = agent.ask("What is Python?")
print(answer)

# 多轮对话（相同 thread_id 保持上下文）
agent.ask("My name is Alice", thread_id="conversation1")
agent.ask("What's my name?", thread_id="conversation1")  # 会记住上一轮

# 获取对话历史
history = agent.get_conversation_history(thread_id="conversation1")
```

## 📊 Phoenix 追踪

1. 启动 Agent 后，控制台会显示 Phoenix URL
2. 在浏览器打开 `http://localhost:6006`
3. 可以看到：
   - 所有 LLM 调用的实时追踪
   - 每个请求的输入/输出
   - 性能指标（延迟、token 使用等）
   - LangGraph 节点执行流程

## 🛡️ 中间件功能

### 1. 日志中间件
- 自动记录所有请求和响应
- 显示时间戳和消息内容
- 调用计数

### 2. Token 预算中间件
- 防止超出预算
- 实时显示 token 使用情况
- 请求数量限制

### 3. 安全过滤中间件
- 自动检测和屏蔽敏感信息：
  - 邮箱地址
  - 电话号码
  - API 密钥
  - 信用卡号

示例：
```
用户输入: "My email is test@example.com"
实际发送: "My email is [REDACTED_EMAIL]"
```

## 🏗️ 项目结构

```
Middleware/
├── qa_agent.py              # QA Agent 实现（LangGraph）
├── core_middleware.py       # 核心中间件
├── phoenix_tracer.py        # Phoenix 追踪器
├── run_agent.py            # 启动脚本
├── .env.example            # 环境变量模板
├── pyproject.toml          # 项目配置
└── QUICKSTART.md           # 本文档
```

## 🔍 核心组件说明

### QAAgent
- 基于 LangGraph 的状态图
- 自动应用中间件链
- 支持多轮对话和状态持久化

### MiddlewareChain
- 管理多个中间件的执行顺序
- `before_invoke`: 调用模型前执行
- `after_invoke`: 模型返回后执行（逆序）

### LangGraph 流程

```
用户输入
  ↓
[middleware_before] → 应用所有 before_invoke 中间件
  ↓
[call_model] → 调用 DeepSeek 模型
  ↓
[middleware_after] → 应用所有 after_invoke 中间件（逆序）
  ↓
返回结果
```

## ⚡ 性能优化

- 使用 DeepSeek：高性价比，适合大量调用
- LangGraph 状态持久化：避免重复加载上下文
- 中间件缓存：减少重复计算

## 🐛 故障排除

### 1. API Key 错误
```
❌ Failed to initialize agent: Error code: 401
```
**解决**：检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确

### 2. Phoenix 启动失败
```
[PHOENIX WARNING] Failed to start Phoenix
```
**解决**：Phoenix 是可选的，不影响 Agent 功能。如需使用，检查端口 6006 是否被占用。

### 3. Token 预算超限
```
❌ Token budget exceeded!
```
**解决**：增加 `max_tokens` 参数或减少对话轮数

## 📚 扩展开发

### 添加自定义中间件

```python
# 在 core_middleware.py 中添加

class CustomMiddleware:
    def before_invoke(self, messages: list) -> list:
        # 在调用模型前执行
        print("Custom processing before model call")
        return messages

    def after_invoke(self, response) -> Any:
        # 在模型返回后执行
        print("Custom processing after model call")
        return response

# 使用
from core_middleware import CustomMiddleware

agent = QAAgent(...)
agent.middleware_chain.add_middleware(CustomMiddleware())
```

### 切换模型

```python
# 使用 OpenAI
agent = QAAgent(model_provider="openai")

# 使用 DeepSeek（默认）
agent = QAAgent(model_provider="deepseek")
```

## 💡 使用技巧

1. **查看统计信息**：聊天时输入 `stats`
2. **多线程对话**：使用不同的 `thread_id` 管理多个独立对话
3. **调试模式**：设置 `enable_logging=True` 查看详细日志
4. **成本控制**：根据需求调整 `max_tokens` 和 `max_requests`

## 🔗 相关资源

- [DeepSeek API 文档](https://platform.deepseek.com/docs)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Arize Phoenix 文档](https://docs.arize.com/phoenix)

---

**现在开始使用吧！**🎉

```bash
python run_agent.py
```
