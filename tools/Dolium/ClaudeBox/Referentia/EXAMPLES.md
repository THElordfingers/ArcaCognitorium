# ClaudeBox — Examples & Cookbook

Real-world patterns for common use cases. Copy, paste, adapt.

---

## Table of Contents

1. [Basic Chat CLI](#1-basic-chat-cli)
2. [Streaming Chat CLI](#2-streaming-chat-cli)
3. [Multi-Agent Sessions](#3-multi-agent-sessions)
4. [Tool Use — Web Search + Calculator](#4-tool-use--web-search--calculator)
5. [Vision — Analyze Multiple Images](#5-vision--analyze-multiple-images)
6. [Document Q&A with Files API](#6-document-qa-with-files-api)
7. [Batch Summarization](#7-batch-summarization)
8. [Extended Thinking — Hard Problems](#8-extended-thinking--hard-problems)
9. [Tkinter Chat App](#9-tkinter-chat-app)
10. [FastAPI Chat Endpoint](#10-fastapi-chat-endpoint)
11. [Logging All Token Usage](#11-logging-all-token-usage)
12. [Rate Limit Handling with Backoff](#12-rate-limit-handling-with-backoff)
13. [One-Shot Query Pattern](#13-one-shot-query-pattern)
14. [Structured Output via Tool Use](#14-structured-output-via-tool-use)
15. [Context-Aware System Prompts per Session](#15-context-aware-system-prompts-per-session)

---

## 1. Basic Chat CLI

```python
from claudebox import ClaudeBox

box = ClaudeBox()

print("ClaudeBox Chat — type 'quit' to exit\n")
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        break
    response = box.send(user_input, stream=False)
    print(f"Claude: {response.text}\n")
```

---

## 2. Streaming Chat CLI

```python
import sys
from claudebox import ClaudeBox

box = ClaudeBox()

print("ClaudeBox Streaming Chat — type 'quit' to exit\n")
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        break

    print("Claude: ", end="", flush=True)
    for token in box.stream(user_input):
        print(token, end="", flush=True)
    print("\n")
```

---

## 3. Multi-Agent Sessions

Run two agents with different personas simultaneously, routing messages independently.

```python
from claudebox import ClaudeBox

box = ClaudeBox()

box.create_session(
    "optimist",
    system_prompt="You are an enthusiastic optimist. Always find the silver lining.",
    model="claude-haiku-4-5-20251001",
)
box.create_session(
    "skeptic",
    system_prompt="You are a critical skeptic. Always question assumptions.",
    model="claude-haiku-4-5-20251001",
)

topic = "The rise of artificial intelligence will be mostly positive for humanity."

optimist_response = box.send(f"What do you think about this: {topic}", session_id="optimist")
skeptic_response = box.send(f"What do you think about this: {topic}", session_id="skeptic")

print("OPTIMIST:", optimist_response.text)
print()
print("SKEPTIC:", skeptic_response.text)
```

---

## 4. Tool Use — Web Search + Calculator

```python
import json
import math
from claudebox import ClaudeBox

box = ClaudeBox()

@box.tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A valid Python math expression, e.g. "2 ** 10" or "math.sqrt(144)"
    """
    try:
        result = eval(expression, {"math": math, "__builtins__": {}})
        return json.dumps({"result": result, "expression": expression})
    except Exception as e:
        return json.dumps({"error": str(e)})

@box.tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price for a ticker symbol.
    
    Args:
        ticker: Stock ticker symbol, e.g. "AAPL" or "GOOGL"
    """
    # In a real implementation, call a financial API here
    prices = {"AAPL": 182.50, "GOOGL": 141.20, "MSFT": 378.90}
    price = prices.get(ticker.upper())
    if price is None:
        return json.dumps({"error": f"Unknown ticker: {ticker}"})
    return json.dumps({"ticker": ticker.upper(), "price": price, "currency": "USD"})

# Subscribe to see what tools Claude calls
box.on_tool_call(lambda t: print(f"  [tool] {t.name}({t.input})"))
box.on_tool_result(lambda r: print(f"  [result] {r.output}"))

response = box.send(
    "If I bought 15 shares of AAPL and 8 shares of MSFT today, "
    "what would my total portfolio value be?"
)
print("\nClaude:", response.text)
```

---

## 5. Vision — Analyze Multiple Images

```python
import base64
from pathlib import Path
from claudebox import ClaudeBox, ImageBlock, ImageSource, TextBlock

box = ClaudeBox()

def load_image(path: str) -> ImageBlock:
    data = base64.standard_b64encode(Path(path).read_bytes()).decode()
    suffix = Path(path).suffix.lower()
    media_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    return ImageBlock(source=ImageSource(
        type="base64",
        media_type=media_map.get(suffix, "image/jpeg"),
        data=data,
    ))

response = box.send([
    TextBlock(text="I have two product photos. Please compare them:"),
    TextBlock(text="Product A:"),
    load_image("product_a.jpg"),
    TextBlock(text="Product B:"),
    load_image("product_b.jpg"),
    TextBlock(text="Which product looks more professionally photographed and why?"),
])

print(response.text)
```

---

## 6. Document Q&A with Files API

Upload a document once, ask many questions without re-uploading.

```python
from pathlib import Path
from claudebox import ClaudeBox, DocumentBlock, DocumentSource, TextBlock

# Enable Files API in claudebox.config.yaml:
# files:
#   enabled: true

box = ClaudeBox()

# Upload once
uploaded = box.upload_file(Path("annual_report_2024.pdf"))
print(f"Uploaded: {uploaded.file_id}")

# Ask multiple questions — file is referenced by ID each time, not re-uploaded
questions = [
    "What was total revenue in 2024?",
    "What were the main risk factors mentioned?",
    "Summarize the CEO's letter to shareholders.",
    "What are the company's goals for 2025?",
]

for question in questions:
    response = box.send(
        [
            DocumentBlock(source=DocumentSource(type="file", file_id=uploaded.file_id)),
            TextBlock(text=question),
        ],
        stream=False,
    )
    print(f"Q: {question}")
    print(f"A: {response.text}\n")

# Clean up
box.delete_file(uploaded.file_id)
```

---

## 7. Batch Summarization

Summarize 50 articles in parallel for a fraction of the cost of individual requests.

```python
from claudebox import ClaudeBox, BatchRequest

box = ClaudeBox()

articles = [
    {"id": "article_001", "text": "The global economy showed signs of recovery..."},
    {"id": "article_002", "text": "Scientists announced a breakthrough in..."},
    # ... 48 more
]

requests = [
    BatchRequest(
        custom_id=article["id"],
        content=f"Summarize this article in 2 sentences:\n\n{article['text']}",
        max_tokens=100,
        model="claude-haiku-4-5-20251001",
    )
    for article in articles
]

# Monitor progress
box.on_batch_poll(lambda s: print(f"Batch status: {s.processing_status}"))
box.on_batch_result(lambda r: print(f"  {r.custom_id}: complete"))

results = box.run_batch(requests)

summaries = {}
for result in results:
    if result.response:
        summaries[result.custom_id] = result.response.text
    else:
        summaries[result.custom_id] = f"ERROR: {result.error}"

for article_id, summary in summaries.items():
    print(f"{article_id}: {summary}\n")
```

---

## 8. Extended Thinking — Hard Problems

```python
from claudebox import ClaudeBox

box = ClaudeBox()

# Enable thinking just for this request
response = box.send(
    """
    A hospital has three doctors and must schedule them for a 7-day week.
    Each doctor needs at least 2 days off. No doctor can work more than 4 consecutive days.
    At least one doctor must be on duty every day.
    Find a valid schedule.
    """,
    thinking_enabled=True,
    thinking_budget_tokens=12000,
    stream=False,
)

print("=== THINKING ===")
print(response.thinking)
print()
print("=== ANSWER ===")
print(response.text)
print()
print(f"Thinking tokens used: {response.usage.input_tokens}")
```

---

## 9. Tkinter Chat App

```python
import tkinter as tk
from tkinter import scrolledtext, font
from claudebox import ClaudeBox

box = ClaudeBox()

def send_message(event=None):
    user_text = entry.get().strip()
    if not user_text:
        return
    
    entry.delete(0, tk.END)
    entry.config(state="disabled")
    send_btn.config(state="disabled")
    
    # Display user message
    chat.config(state="normal")
    chat.insert(tk.END, f"You: {user_text}\n\n", "user")
    chat.insert(tk.END, "Claude: ", "label")
    chat.config(state="disabled")
    chat.see(tk.END)

    def on_token(t):
        chat.after(0, lambda token=t.text: _append(token))

    def on_complete(response):
        chat.after(0, _done)

    def on_error(err):
        chat.after(0, lambda: _error(str(err)))

    def _append(text):
        chat.config(state="normal")
        chat.insert(tk.END, text)
        chat.config(state="disabled")
        chat.see(tk.END)

    def _done():
        chat.config(state="normal")
        chat.insert(tk.END, "\n\n")
        chat.config(state="disabled")
        entry.config(state="normal")
        send_btn.config(state="normal")
        entry.focus()

    def _error(msg):
        chat.config(state="normal")
        chat.insert(tk.END, f"[Error: {msg}]\n\n", "error")
        chat.config(state="disabled")
        entry.config(state="normal")
        send_btn.config(state="normal")

    box.send_threaded(user_text, on_token=on_token, on_complete=on_complete, on_error=on_error)

# Build UI
root = tk.Tk()
root.title("ClaudeBox Chat")
root.geometry("700x550")
root.configure(bg="#1a1a2e")

chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), bg="#16213e", fg="#e0e0e0",
                                  insertbackground="white", state="disabled", relief="flat", padx=10, pady=10)
chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
chat.tag_config("user", foreground="#7ec8e3", font=("Arial", 12, "bold"))
chat.tag_config("label", foreground="#a8dadc", font=("Arial", 12, "bold"))
chat.tag_config("error", foreground="#e63946")

frame = tk.Frame(root, bg="#1a1a2e")
frame.pack(fill=tk.X, padx=10, pady=(5, 10))

entry = tk.Entry(frame, font=("Arial", 12), bg="#0f3460", fg="white", insertbackground="white",
                 relief="flat", bd=8)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
entry.bind("<Return>", send_message)

send_btn = tk.Button(frame, text="Send", command=send_message, font=("Arial", 11, "bold"),
                     bg="#533483", fg="white", activebackground="#7b52ab", relief="flat", padx=12, pady=6)
send_btn.pack(side=tk.RIGHT)

entry.focus()
root.mainloop()
```

---

## 10. FastAPI Chat Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from claudebox import ClaudeBox
import asyncio

app = FastAPI()
box = ClaudeBox()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
async def chat(req: ChatRequest):
    response = await box.send_async(req.message, session_id=req.session_id, stream=False)
    return {"text": response.text, "usage": {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }}

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def generate():
        async for token in box.stream_async(req.message, session_id=req.session_id):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    box.delete_session(session_id)
    return {"deleted": session_id}
```

---

## 11. Logging All Token Usage

Track spend across sessions in real time.

```python
from claudebox import ClaudeBox, TokenUsage

box = ClaudeBox()

total_usage = TokenUsage()

def track_usage(usage: TokenUsage):
    global total_usage
    total_usage = total_usage + usage
    print(
        f"  Request: {usage.input_tokens} in / {usage.output_tokens} out  |  "
        f"Session total: {total_usage.total_tokens} tokens"
    )

box.on_token_usage(track_usage)

box.send("What is machine learning?")
box.send("Give me an example of supervised learning.")
box.send("What about unsupervised learning?")

print(f"\nFinal total: {total_usage.input_tokens} input / {total_usage.output_tokens} output tokens")
```

---

## 12. Rate Limit Handling with Backoff

```python
import time
from claudebox import ClaudeBox, RateLimitError, APIConnectionError

box = ClaudeBox()

def send_with_retry(content: str, max_attempts: int = 5) -> str:
    for attempt in range(max_attempts):
        try:
            response = box.send(content, stream=False)
            return response.text
        except RateLimitError as e:
            wait = e.retry_after or (2 ** attempt)
            print(f"Rate limited. Waiting {wait:.0f}s... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(wait)
        except APIConnectionError as e:
            wait = 2 ** attempt
            print(f"Connection error. Retrying in {wait}s... ({e})")
            time.sleep(wait)

    raise RuntimeError(f"Failed after {max_attempts} attempts")

# Or use the event bus for centralized handling
box.on_rate_limit(lambda e: time.sleep(e.retry_after or 30))
box.on_api_error(lambda e: print(f"API error [{e.status_code}]: {e.message}"))
```

---

## 13. One-Shot Query Pattern

Disable history — each send is independent.

```python
from claudebox import ClaudeBox

# Option A: config
# conversation:
#   auto_clear_after_turn: true

# Option B: clear manually
box = ClaudeBox()

def ask(question: str) -> str:
    response = box.send(question, stream=False)
    box.clear_history()
    return response.text

print(ask("What is the boiling point of water in Celsius?"))
print(ask("Who wrote Hamlet?"))
print(ask("What is 17 * 23?"))
# Each question is completely independent — no history contamination
```

---

## 14. Structured Output via Tool Use

Force Claude to return structured data by making a tool the only output mechanism.

```python
import json
from claudebox import ClaudeBox

box = ClaudeBox()

structured_results = []

@box.tool
def submit_analysis(
    sentiment: str,
    confidence: float,
    key_topics: list,
    summary: str,
) -> str:
    """Submit the analysis result.
    
    Args:
        sentiment: Overall sentiment — "positive", "negative", or "neutral"
        confidence: Confidence score from 0.0 to 1.0
        key_topics: List of main topics discussed
        summary: One-sentence summary of the content
    """
    result = {
        "sentiment": sentiment,
        "confidence": confidence,
        "key_topics": key_topics,
        "summary": summary,
    }
    structured_results.append(result)
    return "Analysis submitted successfully."

articles = [
    "The new product launch exceeded all expectations, with record sales...",
    "The company reported a significant decline in quarterly earnings...",
    "Market analysts remain divided on the outlook for technology stocks...",
]

for article in articles:
    box.send(
        f"Analyze the sentiment and key themes in this article: {article}",
        tool_choice="submit_analysis",   # force use of this specific tool
        stream=False,
        session_id=None,
    )
    box.clear_history()

for result in structured_results:
    print(result)
```

---

## 15. Context-Aware System Prompts per Session

Each session gets a specialized persona based on who's using it.

```python
from claudebox import ClaudeBox

box = ClaudeBox()

users = [
    {"id": "user_123", "role": "developer", "language": "Python", "experience": "senior"},
    {"id": "user_456", "role": "student", "subject": "biology", "level": "undergraduate"},
    {"id": "user_789", "role": "executive", "industry": "finance", "style": "concise"},
]

for user in users:
    session_id = user["id"]
    
    if user["role"] == "developer":
        system = (
            f"You are an expert {user['language']} assistant helping a {user['experience']}-level developer. "
            f"Provide code examples. Be technical. Skip basic explanations."
        )
    elif user["role"] == "student":
        system = (
            f"You are a patient tutor helping an {user['level']} {user['subject']} student. "
            f"Use clear explanations, analogies, and check for understanding."
        )
    else:
        system = (
            f"You are a senior advisor to a {user['industry']} executive. "
            f"Be {user['style']}. Lead with the bottom line. Use bullet points."
        )

    box.create_session(session_id, system_prompt=system)

# Now each session responds differently to the same question
question = "Explain how machine learning models learn from data."

for user in users:
    response = box.send(question, session_id=user["id"], stream=False)
    print(f"\n=== {user['role'].upper()} ===")
    print(response.text[:300] + "...")
```
