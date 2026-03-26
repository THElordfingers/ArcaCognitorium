"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██ ███    ██ ████████ ███████ ██████  ██    ██ ██ ███████ ██     ██ ███████ ██████  ▍
🮈  ██ ████   ██    ██    ██      ██   ██ ██    ██ ██ ██      ██     ██ ██      ██   ██ ▍
🮈  ██ ██ ██  ██    ██    █████   ██████  ██    ██ ██ █████   ██  █  ██ █████   ██████  ▍
🮈  ██ ██  ██ ██    ██    ██      ██   ██  ██  ██  ██ ██      ██ ███ ██ ██      ██   ██ ▍
🮈  ██ ██   ████    ██    ███████ ██   ██   ████   ██ ███████  ███ ███  ███████ ██   ██ ▍
🮈                                                                                      ▍
🮈                                                                                      ▍
🮈                                    Python Script                                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
                                                                                     """
# =============================================================================
# INCITAMENTUM — interviewer.py
# Version: 2.0
# Arca Cognitorium — AI interview engine. Owns the ClaudeBox session.
# =============================================================================

import time
import os
from claudebox import ClaudeBox
from renderer import Renderer
from session_types import SessionType

PROMPT_READY_SENTINEL = '<<<PROMPT_READY>>>'
PROMPT_BLOCK_START    = '<<<PROMPT_START>>>'
PROMPT_BLOCK_END      = '<<<PROMPT_END>>>'
MAX_RETRIES           = 2
RETRY_BACKOFF_S       = 2.0

# Maximum turns before the Interviewer is forced to assemble regardless
MAX_TURNS = 12

SYSTEM_TEMPLATE = """\
You are the INCITAMENTUM Interviewer — an AI assistant embedded in the Arca Cognitorium \
development environment. Your sole purpose is to interview the Wizard (LordFingers) and \
construct a precise Builder session prompt.

CONTEXT:
{context_block}

SESSION TYPE: {session_key}
{system_frag}

INTERVIEW RULES:
- Ask one focused question at a time. Do not stack multiple questions.
- Be direct and terse. The Wizard's time is valuable.
- Ask only what you need. Do not ask for information already provided.
- When you have enough to construct a complete, unambiguous prompt: assemble it.
- Do not ask more than {max_turns} questions total before assembling.

ASSEMBLY SIGNAL:
When ready to assemble, output EXACTLY this structure — no prose before or after:

{sentinel}
{block_start}
<the complete, formatted Builder session prompt here>
{block_end}

The assembled prompt must follow The Builder's session prompt format exactly:
- First line: the session state (e.g. ::BUILD or ::INIT)
- Blank line
- Relevant fields: Repository, Files in scope, Session state (for INIT), Focus, Constraints
- Any additional context the Wizard provided
- No preamble. No explanation. No metadata. Just the prompt the Wizard will paste.
""".format(
    context_block='{context_block}',
    session_key='{session_key}',
    system_frag='{system_frag}',
    max_turns=MAX_TURNS,
    sentinel=PROMPT_READY_SENTINEL,
    block_start=PROMPT_BLOCK_START,
    block_end=PROMPT_BLOCK_END,
)


class InterviewAborted(Exception):
    """Raised when the Wizard cancels mid-interview."""
    pass


class InterviewerFailed(Exception):
    """Raised when all retries are exhausted."""
    pass


class Interviewer:
    """
    Manages one prompt-construction interview.
    One ClaudeBox instance per run(). Multi-turn via box.stream().
    """

    def __init__(
        self,
        session_type: SessionType,
        config:       dict,
        renderer:     Renderer,
    ) -> None:
        self.session_type = session_type
        self.config       = config
        self.renderer     = renderer
        self.box: ClaudeBox | None = None
        self.transcript:  list[dict] = []  # {role, content} for partial saves
        self.turn_count   = 0

    # ── Public ────────────────────────────────────────────────────────────────

    def run(self) -> str | None:
        """
        Run the interview. Returns assembled prompt string, or None on cancel/fail.
        Caller is responsible for catching KeyboardInterrupt at the outer level;
        this method handles it gracefully and returns None.
        """
        system  = self._build_system_prompt()
        api_key = os.environ.get('CLAUDE_API_KEY')
        self.box = ClaudeBox(system_prompt=system, api_key=api_key)

        try:
            return self._interview_loop()
        except KeyboardInterrupt:
            return self._handle_cancel()
        except InterviewerFailed as e:
            self.renderer.print_error(str(e))
            return self._offer_fallback()

    # ── Private ───────────────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        """Construct Interviewer system prompt from session type + config context."""
        repo = self.config.get('repo_url', '(not configured)')
        context_block = f'Repository base URL: {repo}'

        return SYSTEM_TEMPLATE.format(
            context_block = context_block,
            session_key   = self.session_type['key'],
            system_frag   = self.session_type['system_frag'],
        )

    def _interview_loop(self) -> str:
        """
        Drive Q&A turns until sentinel is detected in the AI response.
        Opens with a silent kick-start message so the AI asks the first question.
        Returns the extracted prompt string.
        """
        # Kick-start: tell the AI to begin the interview
        kickstart = (
            f'Begin the interview for a {self.session_type["key"]} session. '
            f'Ask your first question.'
        )

        full_response = self._stream_turn(kickstart, display=False)

        while True:
            self.turn_count += 1

            if PROMPT_READY_SENTINEL in full_response:
                prompt = self._extract_prompt(full_response)
                if prompt:
                    return prompt
                # Sentinel present but extraction failed — ask AI to retry
                full_response = self._stream_turn(
                    'Your assembly markers were malformed. Please output the assembled prompt again, '
                    f'using exactly {PROMPT_READY_SENTINEL}, {PROMPT_BLOCK_START}, {PROMPT_BLOCK_END}.',
                    display=False,
                )
                prompt = self._extract_prompt(full_response)
                return prompt or ''

            # Display the AI's question inside the interviewer box
            self.renderer.interviewer_box_open()
            # Re-stream the already-accumulated response visually
            for line in full_response.splitlines():
                print(f'  \033[38;2;169;143;212m│\033[0m  {line}')
            self.renderer.interviewer_box_close()

            # Get Wizard input
            user_input = self.renderer.wizard_prompt()
            if not user_input:
                # Empty input — gentle re-prompt once
                self.renderer.print_warning('No input received. Type your response or Ctrl+C to cancel.')
                user_input = self.renderer.wizard_prompt()
                if not user_input:
                    raise KeyboardInterrupt

            self.transcript.append({'role': 'user', 'content': user_input})

            # Force assembly after MAX_TURNS
            if self.turn_count >= MAX_TURNS:
                user_input += (
                    f'\n\n[System: You have reached the maximum turn limit. '
                    f'Assemble the prompt now using the {PROMPT_READY_SENTINEL} sentinel.]'
                )

            full_response = self._stream_turn(user_input)

    def _stream_turn(self, content: str, display: bool = True) -> str:
        """
        Send one turn via box.stream(). If display=True, renders inside the
        interviewer box with live token streaming. Returns full response string.
        Retries up to MAX_RETRIES on failure.
        """
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            if attempt > 0:
                self.renderer.print_warning(
                    f'Retrying... (attempt {attempt + 1} of {MAX_RETRIES + 1})'
                )
                time.sleep(RETRY_BACKOFF_S * attempt)

            try:
                if display:
                    self.renderer.interviewer_box_open()
                    token_iter = self.box.stream(content)
                    result = self.renderer.stream_tokens(token_iter)
                    self.renderer.interviewer_box_close()
                else:
                    # Silent accumulation — used for kickstart and retries
                    result = ''.join(self.box.stream(content))

                self.transcript.append({'role': 'assistant', 'content': result})
                return result

            except Exception as e:
                last_error = e
                continue

        raise InterviewerFailed(
            f'The Interviewer fell silent after {MAX_RETRIES + 1} attempts. '
            f'Last error: {last_error}'
        )

    def _extract_prompt(self, response: str) -> str:
        """
        Extract the assembled prompt block between PROMPT_BLOCK_START and PROMPT_BLOCK_END.
        Returns stripped prompt string, or empty string if markers not found.
        """
        start = response.find(PROMPT_BLOCK_START)
        end   = response.find(PROMPT_BLOCK_END)
        if start == -1 or end == -1 or end <= start:
            return ''
        return response[start + len(PROMPT_BLOCK_START):end].strip()

    def _handle_cancel(self) -> None:
        """Offer save-partial or discard on KeyboardInterrupt."""
        self.renderer.print_cancelled()
        if self.transcript:
            self.renderer.print_warning(
                'Interview transcript exists. It will be saved to history as "abandoned".'
            )
        return None

    def _offer_fallback(self) -> None:
        """On total failure, inform Wizard. No automatic fallback to v1 — just clean exit."""
        self.renderer.print_error(
            'Interview could not be completed. Check CLAUDE_API_KEY and network, then retry.'
        )
        return None

    # ── Accessors for outer layer ─────────────────────────────────────────────

    @property
    def partial_transcript(self) -> list[dict]:
        return list(self.transcript)
