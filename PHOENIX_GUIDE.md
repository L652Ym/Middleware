# Phoenix 追踪使用指南

## 🎯 两种模式对比

### 模式 1：External（外部）模式 ✅ 推荐 Windows

**工作原理**：
- Phoenix 服务器单独运行
- Agent 连接到已存在的 Phoenix 服务器
- **Windows 兼容** ✅

**优点**：
- ✅ Windows 完全兼容
- ✅ Phoenix 服务器稳定运行
- ✅ 可以在多个 Agent 之间共享
- ✅ 与你之前的代码一样工作

### 模式 2：Embedded（内嵌）模式 ⚠️ 仅 Linux/Mac

**工作原理**：
- Phoenix 在 Agent 进程内启动
- 自动管理 Phoenix 生命周期

**缺点**：
- ❌ Windows 上可能失败（DNS 错误）
- ⚠️ 每次运行 Agent 都启动新的 Phoenix 实例

---

## 🚀 快速开始：External 模式（推荐）

### 步骤 1：配置 `.env`

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat

# Phoenix 配置（外部模式）
PHOENIX_ENABLED=true
PHOENIX_MODE=external
PHOENIX_HOST=127.0.0.1
PHOENIX_PORT=6006
```

### 步骤 2：启动 Phoenix 服务器

打开**第一个终端**，启动 Phoenix：

```bash
# 方式 1：使用 phoenix 命令（如果已安装）
python -m phoenix.server.main serve

# 方式 2：或使用 phoenix CLI
phoenix serve
```

你应该看到：

```
🌍 Phoenix server running on http://localhost:6006
```

### 步骤 3：运行 Agent

打开**第二个终端**，运行 Agent：

```bash
python main.py
```

你会看到：

```
[PHOENIX] Connecting to external Phoenix server...
[PHOENIX] ✓ Tracer registered successfully
[PHOENIX] Dashboard URL: http://127.0.0.1:6006

✓ Using DeepSeek Chat Model
✓ QA Agent initialized with 3 middleware(s)
```

### 步骤 4：查看追踪

在浏览器打开：http://localhost:6006

你会看到所有 LLM 调用的实时追踪！

---

## 📊 完整示例：像你之前的代码一样

你之前的代码为什么可以工作：

```python
# 你之前的代码（简化版）
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# 连接到外部 Phoenix 服务器
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces"
)

# 监控 LangChain
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

# 使用 LLM
llm = ChatOpenAI(...)
response = llm.invoke("Hello")  # 自动追踪到 Phoenix
```

**现在的代码做同样的事情：**

```python
# 现在的代码（自动化版本）
from qa_agent import QAAgent
from phoenix_tracer import init_phoenix

# 初始化 Phoenix（外部模式）
phoenix = init_phoenix()  # 从 .env 读取配置

# 创建 Agent（自动被追踪）
agent = QAAgent(model_provider="deepseek")

# 使用 Agent
answer = agent.ask("Hello")  # 自动追踪到 Phoenix
```

两者完全等价，只是现在的代码更自动化！

---

## 🔧 配置选项

### 选项 1：禁用 Phoenix（最简单）

```env
PHOENIX_ENABLED=false
```

Agent 正常工作，没有追踪。

### 选项 2：External 模式（推荐）

```env
PHOENIX_ENABLED=true
PHOENIX_MODE=external  # 关键！
```

然后单独启动 Phoenix：
```bash
python -m phoenix.server.main serve
```

### 选项 3：Embedded 模式（Linux/Mac）

```env
PHOENIX_ENABLED=true
PHOENIX_MODE=embedded
```

Phoenix 自动启动（Windows 上可能失败）。

---

## 💡 常见场景

### 场景 1：开发时调试（有追踪）

**终端 1（Phoenix）：**
```bash
python -m phoenix.server.main serve
```

**终端 2（Agent）：**
```bash
# .env: PHOENIX_ENABLED=true, PHOENIX_MODE=external
python main.py
```

### 场景 2：生产运行（无追踪）

```bash
# .env: PHOENIX_ENABLED=false
python main.py
```

### 场景 3：快速测试（无追踪）

```bash
# 临时禁用 Phoenix
PHOENIX_ENABLED=false python main.py
```

---

## 🐛 故障排除

### 错误：Phoenix 服务器未启动

```
[PHOENIX WARNING] External Phoenix server not reachable
```

**解决**：
1. 检查 Phoenix 是否在运行：浏览器访问 http://localhost:6006
2. 启动 Phoenix：`python -m phoenix.server.main serve`

### 错误：端口被占用

```
ERROR: Port 6006 is already in use
```

**解决**：
```bash
# 使用不同端口
python -m phoenix.server.main serve --port 6007

# 然后更新 .env
PHOENIX_PORT=6007
```

### 错误：Windows DNS 失败（之前的问题）

```
[Errno 11001] getaddrinfo failed
```

**解决**：使用 External 模式
```env
PHOENIX_MODE=external  # 改为 external
```

---

## 📈 最佳实践

### ✅ 推荐做法

1. **开发环境**：
   - 使用 External 模式
   - 单独运行 Phoenix 服务器
   - 可以随时重启 Agent 而不影响追踪历史

2. **生产环境**：
   - 禁用 Phoenix（`PHOENIX_ENABLED=false`）
   - 或使用专用的 Phoenix 服务器
   - 使用 LoggingMiddleware 记录到文件

3. **Windows 用户**：
   - 始终使用 External 模式
   - 避免 Embedded 模式

### ❌ 避免做法

- ❌ Windows 上使用 Embedded 模式
- ❌ 生产环境使用 Embedded 模式
- ❌ 忘记启动 Phoenix 服务器（External 模式）

---

## 🎓 深入理解

### 为什么 External 模式更好？

1. **稳定性**：Phoenix 服务器独立运行，不受 Agent 影响
2. **共享**：多个 Agent 可以连接到同一个 Phoenix
3. **历史**：重启 Agent 不丢失追踪历史
4. **兼容性**：Windows 完全支持

### 追踪流程

```
Agent 代码
    ↓
LangChain 调用
    ↓
OpenTelemetry (自动捕获)
    ↓
Phoenix 服务器 (http://localhost:6006)
    ↓
Web 界面显示
```

---

## 🔗 相关资源

- Phoenix 文档：https://docs.arize.com/phoenix
- OpenTelemetry：https://opentelemetry.io/
- LangChain 追踪：https://python.langchain.com/docs/guides/tracing

---

**推荐配置（Windows）：**

```env
PHOENIX_ENABLED=true
PHOENIX_MODE=external
PHOENIX_HOST=127.0.0.1
PHOENIX_PORT=6006
```

```bash
# 终端 1
python -m phoenix.server.main serve

# 终端 2
python main.py
```

这样就和你之前的代码一样工作了！🎉
