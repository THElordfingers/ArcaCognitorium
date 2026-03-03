#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    gpt-client/client/chat_client.py 
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import time
from typing import Dict, List, Optional

from client.config import AppConfig
from client.renderer import Renderer
from client.router import ModelRouter
from client.logger import ImmutableLogger
from client.input_processor import InputProcessor

from memory.vector_store import VectorStore
from memory.summarizer import Summarizer
from memory.conversation_store import ConversationStore
from client.analytics import AnalyticsEngine
from memory.file_ingest import TextFileIngestor


class ChatClient:
    def __init__(self, cfg: AppConfig, *, api_key: str):
        self.cfg = cfg

        self.renderer = Renderer(cfg)
        self.router = ModelRouter(cfg, api_key=api_key)
        self.logger = ImmutableLogger(cfg)
        self.input = InputProcessor()

        # Share the OpenAI client instance across modules
        self.oa_client = self.router.client

        self.vectors = VectorStore(cfg, client=self.oa_client)
        self.summarizer = Summarizer(cfg, client=self.oa_client)
        self.conversations = ConversationStore(cfg, summarizer=self.summarizer)

        self.analytics = AnalyticsEngine(cfg, client=self.oa_client, vectors=self.vectors)
        self.ingestor = TextFileIngestor(cfg)

        self._forced_bucket: Optional[str] = None  # e.g. "smart" for next turn only

    def run(self):
        self.renderer.banner()
        self.renderer.system(f"Active conversation: {self.conversations.active.id}")

        while True:
            try:
                raw = input("> ")
                parsed = self.input.parse(raw)

                if parsed.kind == "text" and not parsed.text:
                    continue

                if parsed.kind == "command":
                    if self._handle_command(parsed.command or "", parsed.args or ""):
                        break
                    continue

                # Normal chat text
                user_text = parsed.text
                self.renderer.user(user_text)

                self.conversations.append("user", user_text)
                self.logger.log_message(
                    conversation_id=self.conversations.active.id,
                    role="user",
                    content=user_text,
                    model=None,
                    extra={"summary_present": bool(self.conversations.active.summary)},
                )

                context = self._build_context(user_text)

                forced = self._forced_bucket
                self._forced_bucket = None  # one-shot
                decision = self.router.decide(user_text, forced=forced)

                title = "Assistant"
                if self.cfg.ui.show_model_badge:
                    title = f"Assistant • {decision.model} ({decision.reason})"

                update, close = self.renderer.assistant_stream(title=title)

                gen, meta = self.router.stream_response_text(
                    decision.model,
                    context,
                    temperature=self.cfg.raw.get("temperature", None),
                    max_output_tokens=self.cfg.raw.get("max_output_tokens", None),
                )

                delay = float(self.cfg.ui.typing_delay_seconds)
                for delta in gen:
                    if delay > 0:
                        time.sleep(delay)
                    update(delta)

                assistant_text = close()

                self.conversations.append("assistant", assistant_text)
                self.logger.log_message(
                    conversation_id=self.conversations.active.id,
                    role="assistant",
                    content=assistant_text,
                    model=decision.model,
                    usage=meta.get("usage"),
                    extra={"routing_reason": decision.reason},
                )

                # Add the exchange to long-term memory (vector store)
                self.vectors.add(
                    f"USER: {user_text}\nASSISTANT: {assistant_text}",
                    metadata={"type": "turn", "conversation_id": self.conversations.active.id},
                )

                # Periodic self-analytics (writes into vector store + analytics log)
                self.analytics.observe(
                    conversation_id=self.conversations.active.id,
                    summary=self.conversations.active.summary,
                    last_user=user_text,
                    last_assistant=assistant_text,
                )

            except KeyboardInterrupt:
                self.renderer.system("Interrupted. Type /exit to quit.")
            except Exception as e:
                self.renderer.error(str(e))

    def _build_context(self, user_text: str) -> List[Dict]:
        conv = self.conversations.active
        mem_cfg = self.cfg.memory

        messages: List[Dict] = []

        if conv.summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary (compressed memory):\n{conv.summary}"
            })

        retrieved = self.vectors.query(user_text, top_k=int(mem_cfg.retrieve_top_k))
        if retrieved:
            blob = "\n\n".join(f"[score={r['score']:.3f}] {r['text']}" for r in retrieved)
            messages.append({
                "role": "system",
                "content": "Relevant long-term memory (retrieved):\n" + blob
            })

        short_max = int(mem_cfg.short_term_max_messages)
        for m in conv.messages[-short_max:]:
            messages.append({"role": m["role"], "content": m["content"]})

        if not messages or messages[-1]["role"] != "user" or messages[-1]["content"] != user_text:
            messages.append({"role": "user", "content": user_text})

        return messages

    def _handle_command(self, cmd: str, args: str) -> bool:
        cmd = cmd.strip().lower()

        if cmd in ("/exit", "/quit"):
            self.renderer.system("Goodbye.")
            return True

        if cmd == "/help":
            self.renderer.help()
            return False

        if cmd == "/new":
            conv = self.conversations.new()
            self.renderer.system(f"Started new conversation: {conv.id}")
            return False

        if cmd == "/load":
            if not args:
                self.renderer.error("Usage: /load <conversation_id>")
                return False
            conv = self.conversations.load(args.strip())
            self.renderer.system(f"Loaded conversation: {conv.id} • {conv.title or '(untitled)'}")
            return False

        if cmd == "/menu":
            convos = self.conversations.list()
            self.renderer.menu(convos, active_id=self.conversations.active.id)
            choice = input("Load ID> ").strip()
            if choice:
                conv = self.conversations.load(choice)
                self.renderer.system(f"Loaded conversation: {conv.id} • {conv.title or '(untitled)'}")
            return False

        if cmd == "/remember":
            if not args:
                self.renderer.error("Usage: /remember <text>")
                return False
            self.vectors.add(args, metadata={"type": "manual_note"})
            self.renderer.system("Saved note to long-term memory.")
            return False

        if cmd == "/vaddfile":
            if not args:
                self.renderer.error("Usage: /vaddfile <path/to/file.txt>")
                return False
            res = self.ingestor.ingest_file(args, self.vectors, tag="manual_file")
            self.renderer.system(f"Ingested file:\n{res.path}\nbytes={res.bytes_read} chunks_added={res.chunks_added}")
            return False

        if cmd == "/vadddir":
            if not args:
                self.renderer.error("Usage: /vadddir <path/to/directory>")
                return False
            results = self.ingestor.ingest_dir(args, self.vectors, tag="manual_dir")
            total_files = len(results)
            total_chunks = sum(r.chunks_added for r in results)
            self.renderer.system(f"Ingested directory:\nfiles={total_files} total_chunks={total_chunks}")
            return False

        if cmd == "/vquery":
            if not args:
                self.renderer.error("Usage: /vquery <text>")
                return False
            hits = self.vectors.query(args, top_k=int(self.cfg.memory.retrieve_top_k))
            if not hits:
                self.renderer.system("No relevant vector hits.")
                return False
            text = "\n\n".join([f"{h['score']:.3f} • {h['text']}" for h in hits])
            self.renderer.system("Vector hits:\n" + text)
            return False

        if cmd == "/vdump":
            st = self.vectors.stats()
            self.renderer.system(f"Vector store stats:\n{st}")
            return False

        if cmd == "/smart":
            self._forced_bucket = "smart"
            self.renderer.system("Next turn will use smart model.")
            return False

        self.renderer.error(f"Unknown command: {cmd}. Type /help.")
        return False
