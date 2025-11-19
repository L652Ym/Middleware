# Windows 故障排除指南

## Phoenix 启动失败错误

如果你在 Windows 上遇到这个错误：

```
ERROR: [Errno 11001] getaddrinfo failed
💥 Phoenix failed to start
```

### 快速解决方案

#### 方案 1：禁用 Phoenix（推荐）

编辑你的 `.env` 文件，将 Phoenix 禁用：

```env
PHOENIX_ENABLED=false
```

然后重新运行：

```bash
python main.py
```

Agent 会正常工作，只是没有追踪功能。

#### 方案 2：修复 Phoenix 配置

如果你的 `.env` 文件中 `PHOENIX_HOST` 包含 `http://`，请修改为：

**错误配置：**
```env
PHOENIX_HOST=http://localhost
```

**正确配置：**
```env
PHOENIX_HOST=127.0.0.1
PHOENIX_PORT=6006
```

### 验证修复

运行后应该看到以下之一：

**Phoenix 成功启动：**
```
============================================================
[PHOENIX] Arize Phoenix Started Successfully
[PHOENIX] Dashboard URL: http://127.0.0.1:6006
============================================================
```

**Phoenix 禁用（正常）：**
```
QA Agent initialized with 3 middleware(s)
```

## 常见问题

### 1. 端口被占用

如果看到 "port 6006 is already in use"：

```env
# 使用不同的端口
PHOENIX_PORT=6007
```

### 2. 网络权限问题

Windows 防火墙可能阻止 Phoenix。解决方案：

1. 禁用 Phoenix（方案 1）
2. 或在防火墙中允许 Python

### 3. SQLAlchemy 警告

这些警告可以忽略：
```
SAWarning: Skipped unsupported reflection of expression-based index...
```

它们不影响功能。

## 推荐配置（Windows）

**完整的 `.env` 文件示例：**

```env
# DeepSeek API (必需)
DEEPSEEK_API_KEY=sk-your-actual-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat

# Phoenix 追踪 (可选 - 如果有问题就禁用)
PHOENIX_ENABLED=false
PHOENIX_HOST=127.0.0.1
PHOENIX_PORT=6006
```

## 测试运行

```bash
# 确保在项目目录下
cd Middleware

# 运行 Agent
python main.py

# 或使用 conda/venv
conda activate your-env
python main.py
```

## 仍然有问题？

1. **检查 Python 版本**：
   ```bash
   python --version  # 应该是 3.11+
   ```

2. **重新安装依赖**：
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **查看完整错误日志**：
   启用详细日志并提供完整的错误信息

4. **最简单的解决方案**：
   - 设置 `PHOENIX_ENABLED=false`
   - Agent 的所有核心功能都会正常工作
   - Phoenix 只是可选的监控工具

## 成功运行示例

```
============================================================
  LangGraph QA Agent with Middleware & Phoenix Tracing
============================================================

✓ Using DeepSeek Chat Model
✓ QA Agent initialized with 3 middleware(s)

============================================================
QA Agent - Interactive Chat Mode
============================================================
Type 'quit' or 'exit' to end the conversation
Type 'stats' to see usage statistics
============================================================

You: Hello
```

## 总结

- **Phoenix 是可选的** - 禁用不影响核心功能
- **推荐设置** - Windows 上设置 `PHOENIX_ENABLED=false`
- **核心功能完整** - 所有中间件和 Agent 功能都正常工作
