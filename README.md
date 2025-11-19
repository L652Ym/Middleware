# LangGraph QA Agent with Middleware & Phoenix Tracing

A streamlined question-answering agent built with **LangGraph**, integrated with **middleware** for production-ready control and **Arize Phoenix** for real-time tracing.

## ✨ Features

- 🤖 **LangGraph-based QA Agent**: Stateful, multi-turn conversations
- 🔧 **Production Middleware**: Logging, budget control, security filtering
- 📊 **Phoenix Tracing**: Real-time monitoring and debugging
- 💰 **DeepSeek Integration**: Cost-effective LLM API
- 🔐 **PII Protection**: Automatic redaction of sensitive data
- 💬 **Multi-turn Chat**: Context-aware conversations with state persistence

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Middleware

# Install dependencies
uv sync
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your DeepSeek API key
# DEEPSEEK_API_KEY=sk-your-key-here
```

### 3. Run

```bash
# Interactive chat mode
python main.py

# Or use the direct script
python run_agent.py

# Single question mode
python run_agent.py "What is machine learning?"

# Demo examples
python run_agent.py --demo
```

## 📊 Phoenix Tracing

When you start the agent, Phoenix will launch automatically at `http://localhost:6006`

Open this URL in your browser to see:
- Real-time traces of all LLM calls
- Performance metrics (latency, tokens)
- LangGraph node execution flow
- Complete input/output logs

## 🏗️ Architecture

```
User Input
    ↓
[Middleware: Before] → Logging, Budget Check, Security Filter
    ↓
[LLM Model] → DeepSeek Chat
    ↓
[Middleware: After] → Post-processing
    ↓
Response
```

## 🛡️ Middleware

### 1. LoggingMiddleware
- Logs all requests and responses
- Timestamps and call counts
- Useful for debugging and auditing

### 2. TokenBudgetMiddleware
- Prevents cost overruns
- Tracks token usage and request counts
- Configurable limits

### 3. SecurityFilterMiddleware
- Automatically detects and redacts PII:
  - Email addresses
  - Phone numbers
  - API keys
  - Credit card numbers

Example:
```
Input:  "My email is test@example.com"
Output: "My email is [REDACTED_EMAIL]"
```

## 💡 Code Usage

```python
from qa_agent import QAAgent
from phoenix_tracer import init_phoenix

# Initialize Phoenix (optional)
phoenix = init_phoenix()

# Create agent
agent = QAAgent(
    model_provider="deepseek",
    enable_logging=True,
    enable_budget=True,
    enable_security=True,
    max_tokens=100000,
    max_requests=200
)

# Single question
answer = agent.ask("What is Python?")

# Multi-turn conversation (same thread_id keeps context)
agent.ask("My name is Alice", thread_id="chat1")
agent.ask("What's my name?", thread_id="chat1")  # Remembers context

# Interactive chat
agent.chat()
```

## 📁 Project Structure

```
Middleware/
├── qa_agent.py              # LangGraph QA Agent (core)
├── core_middleware.py       # Three essential middlewares
├── phoenix_tracer.py        # Phoenix tracing integration
├── run_agent.py            # Main entry script
├── main.py                 # Alternative entry point
├── .env.example            # Environment variables template
├── pyproject.toml          # Project dependencies
└── QUICKSTART.md           # Detailed quick start guide
```

## 🔧 Configuration

Edit `.env` file:

```env
# DeepSeek API (Required)
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_CHAT_MODEL=deepseek-chat

# Phoenix Tracing (Optional)
PHOENIX_ENABLED=true
PHOENIX_HOST=http://localhost
PHOENIX_PORT=6006
```

## 🎯 Use Cases

- **Customer Support Bot**: Multi-turn conversations with context
- **Research Assistant**: Ask follow-up questions naturally
- **Code Helper**: Programming Q&A with memory
- **Educational Tutor**: Patient, context-aware teaching

## 🛠️ Extending

### Add Custom Middleware

```python
from core_middleware import MiddlewareChain

class CustomMiddleware:
    def before_invoke(self, messages):
        # Process before LLM call
        return messages

    def after_invoke(self, response):
        # Process after LLM response
        return response

# Add to agent
agent = QAAgent(...)
agent.middleware_chain.add_middleware(CustomMiddleware())
```

### Switch Models

```python
# Use OpenAI instead of DeepSeek
agent = QAAgent(model_provider="openai")
```

## 📚 Documentation

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for detailed guide
- **DeepSeek API**: https://platform.deepseek.com/docs
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Phoenix**: https://docs.arize.com/phoenix

## 🐛 Troubleshooting

**API Key Error**
```
❌ Failed to initialize agent: Error code: 401
```
→ Check `DEEPSEEK_API_KEY` in `.env`

**Phoenix Won't Start**
```
[PHOENIX WARNING] Failed to start Phoenix
```
→ Phoenix is optional. Check if port 6006 is available or disable with `PHOENIX_ENABLED=false`

**Budget Exceeded**
```
❌ Token budget exceeded!
```
→ Increase `max_tokens` parameter when creating the agent

## 📊 Performance

- **DeepSeek**: Cost-effective, fast responses
- **LangGraph**: Efficient state management
- **Middleware**: Minimal overhead (~1-2ms per call)

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License

---

**Get started now:**

```bash
python main.py
```

For detailed documentation, see [QUICKSTART.md](QUICKSTART.md)
