# ClaudeBox — Quick Start

Get running in 2 minutes.

---

## 1. Install

```bash
pip install anthropic pyyaml
```

## 2. Set your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 3. Drop ClaudeBox into your project

```
your_project/
├── claudebox/              ← copy this folder
├── claudebox.config.yaml   ← copy this file
└── your_script.py
```

## 4. Send your first message

```python
from claudebox import ClaudeBox

box = ClaudeBox()
response = box.send("Hello, Claude!")
print(response.text)
```

---

## Common patterns

### Streaming tokens to the terminal

```python
box = ClaudeBox()
box.on_token(lambda t: print(t.text, end="", flush=True))
box.send("Write me a short poem about the ocean.")
print()
```

### Multi-turn conversation

```python
box = ClaudeBox()
box.send("My name is Alice and I love hiking.")
response = box.send("What's my name and what do I enjoy?")
print(response.text)  # "Your name is Alice and you enjoy hiking."
```

### Register a tool

```python
import json
from claudebox import ClaudeBox

box = ClaudeBox()

@box.tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return json.dumps({"location": location, "temp": "22°C", "condition": "Sunny"})

response = box.send("What's the weather in Paris?")
print(response.text)  # Claude calls the tool and answers naturally
```

### Async

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    box = ClaudeBox()
    response = await box.send_async("Hello!")
    print(response.text)

asyncio.run(main())
```

### Generator streaming

```python
box = ClaudeBox()
for token in box.stream("Tell me a short story."):
    print(token, end="", flush=True)
print()
```

---

## Configure it

Open `claudebox.config.yaml`. Every option is documented inline. Key ones to know:

```yaml
model:
  model: "claude-sonnet-4-6"   # or claude-opus-4-6, claude-haiku-4-5-20251001
  max_tokens: 1024
  temperature: null            # 0.0–1.0

system:
  prompt: null                 # your default system prompt

streaming:
  enabled: true                # false to disable streaming

tools:
  auto_run_tools: true         # false to handle tool calls yourself
  max_tool_iterations: 10

logging:
  level: "warning"             # "debug" to see everything
```

---

For everything else, see **GUIDE.md**.
