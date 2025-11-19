# DeepSeek 和 Phoenix 集成指南

本指南介绍如何在 LangChain 中间件项目中使用 DeepSeek 模型和 Arize Phoenix 追踪功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装依赖（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env`，并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# DeepSeek 模型配置
DEEPSEEK_CHAT_MODEL=deepseek-chat
DEEPSEEK_EMBEDDING_MODEL=deepseek-chat

# Phoenix 追踪配置
PHOENIX_ENABLED=true
PHOENIX_HOST=http://localhost
PHOENIX_PORT=6006
```

### 3. 获取 DeepSeek API 密钥

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账户并登录
3. 进入 API 密钥管理页面
4. 创建新的 API 密钥
5. 将密钥复制到 `.env` 文件中的 `DEEPSEEK_API_KEY`

### 4. 运行演示

```bash
# 运行主程序
python main.py

# 或直接运行 demo
python demo_examples.py
```

## 📊 Arize Phoenix 追踪

### 什么是 Phoenix？

Arize Phoenix 是一个开源的 LLM 可观测性平台，提供：

- 📈 实时追踪 LLM 调用
- 🔍 请求/响应详细日志
- ⚡ 性能指标和分析
- 🎯 错误监控和调试
- 📊 可视化仪表板

### 使用 Phoenix

1. **启动 Phoenix**

   当你运行程序时，Phoenix 会自动启动并显示仪表板 URL：

   ```
   [PHOENIX] Arize Phoenix Started Successfully
   [PHOENIX] Dashboard URL: http://localhost:6006
   ```

2. **打开仪表板**

   在浏览器中打开 `http://localhost:6006`，你将看到：
   - 所有 LLM 调用的跟踪记录
   - 每个请求的详细信息（输入、输出、延迟等）
   - 性能指标和统计信息
   - 错误和异常

3. **禁用 Phoenix**

   如果不想使用追踪功能，在 `.env` 中设置：

   ```env
   PHOENIX_ENABLED=false
   ```

## 🔧 高级配置

### 使用不同的模型提供商

在代码中，你可以选择使用不同的模型：

```python
from demo_examples import MiddlewareDemo

# 使用 DeepSeek（默认）
demo = MiddlewareDemo(model_provider="deepseek")

# 使用 OpenAI
demo = MiddlewareDemo(model_provider="openai")

# 使用 Gemini
demo = MiddlewareDemo(model_provider="gemini")
```

### 自定义 Phoenix 配置

```python
from phoenix_tracer import init_phoenix

# 自定义配置
phoenix = init_phoenix(
    enabled=True,
    host="http://localhost",
    port=6006,
    auto_instrument=True
)
```

### 编程方式初始化

```python
import os
from dotenv import load_dotenv
from demo_examples import MiddlewareDemo
from phoenix_tracer import init_phoenix

# 加载环境变量
load_dotenv()

# 初始化 Phoenix
phoenix = init_phoenix()

# 创建演示实例
demo = MiddlewareDemo(model_provider="deepseek")

# 运行你的代码...
```

## 💡 示例代码

### 基本使用

```python
from demo_examples import MiddlewareDemo
from middleware import LoggingMiddleware
from phoenix_tracer import init_phoenix

# 初始化 Phoenix 追踪
phoenix = init_phoenix()

# 创建 DeepSeek 模型实例
demo = MiddlewareDemo(model_provider="deepseek")

# 使用中间件
logging_mw = LoggingMiddleware(verbose=True)

# 发送消息
messages = [
    {'role': 'system', 'content': 'You are a helpful AI assistant.'},
    {'role': 'user', 'content': 'What is machine learning?'}
]

response = demo.simulate_call_with_middleware(messages, [logging_mw])
print(response.content)
```

### 多中间件堆栈

```python
from middleware import (
    LoggingMiddleware,
    SecurityFilterMiddleware,
    TokenBudgetMiddleware,
    ExpertiseBasedMiddleware,
    UserContext
)

# 创建用户上下文
context = UserContext(user_id="user_001", expertise_level="expert")

# 构建中间件栈
middleware_stack = [
    LoggingMiddleware(verbose=True),
    SecurityFilterMiddleware(),
    TokenBudgetMiddleware(max_tokens=10000),
    ExpertiseBasedMiddleware(context),
]

# 使用完整的中间件栈
response = demo.simulate_call_with_middleware(messages, middleware_stack)
```

## 🐛 故障排除

### DeepSeek API 错误

如果遇到 API 错误：

1. 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确
2. 确认 API 密钥有效且有足够的额度
3. 检查网络连接

### Phoenix 启动失败

如果 Phoenix 无法启动：

1. 检查端口 6006 是否被占用
2. 尝试更改 `.env` 中的 `PHOENIX_PORT`
3. 确认已安装所有依赖：`pip install arize-phoenix arize-phoenix-otel openinference-instrumentation-langchain`

### 依赖安装问题

```bash
# 清理并重新安装
rm -rf .venv uv.lock
uv sync

# 或使用 pip
pip install --upgrade pip
pip install -r requirements.txt
```

## 📚 资源链接

- [DeepSeek 官方文档](https://platform.deepseek.com/docs)
- [Arize Phoenix 文档](https://docs.arize.com/phoenix)
- [LangChain 文档](https://python.langchain.com/)

## 🔍 监控最佳实践

1. **始终启用 Phoenix** - 在开发和测试环境中，始终启用 Phoenix 以便追踪和调试
2. **查看详细追踪** - 在 Phoenix 仪表板中查看每个请求的详细信息
3. **分析性能指标** - 使用 Phoenix 分析延迟、token 使用等指标
4. **错误追踪** - 当出现错误时，在 Phoenix 中查看完整的调用栈

## ⚡ 性能优化

DeepSeek 提供高性价比的 API 服务：

- **deepseek-chat**: 通用对话模型，适合大多数场景
- **成本优势**: 相比 OpenAI 等服务更具性价比
- **速度**: 响应速度快，适合实时应用

## 🔐 安全提示

- **不要提交 .env 文件** - `.env` 文件包含敏感信息，已添加到 `.gitignore`
- **定期轮换 API 密钥** - 定期更换 DeepSeek API 密钥以提高安全性
- **使用环境变量** - 在生产环境中使用环境变量而不是硬编码密钥
