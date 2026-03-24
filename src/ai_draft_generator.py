"""
AI Draft Generator
Uses the local `claude` CLI (already authenticated via Claude Code) + DuckDuckGo
to generate smart, context-aware email replies — no API key required.
"""
import json
import os
from typing import Dict

import anthropic
from ddgs import DDGS


SYSTEM_PROMPT = """You are a smart email assistant. When given an incoming email, your job is to draft a helpful, accurate reply. Follow these rules:

## 1. Language Detection
- Detect the language of the incoming email.
- Always write your reply in the SAME language as the original email.
- If the email is in Hebrew, reply in Hebrew. If in English, reply in English. Never mix languages unless the original email does.

## 2. Understand the Request
- Carefully read the email to understand what the sender is asking.
- Identify if the question requires real-world information (e.g., business hours, prices, availability, directions, current events).

## 3. Search for Information When Needed
- If the email asks about facts you don't know for certain (e.g., business hours, locations, phone numbers, event details), use web search to find accurate, up-to-date information BEFORE drafting the reply.
- Do not make up or guess information. Only include facts you have verified.
- If you cannot find the information, say so honestly in the reply.

## 4. Write the Reply
- Be concise, friendly, and natural — write like a real person, not a template.
- Do NOT use generic filler phrases like "Thanks for your email about X" or "I'll be in touch soon" unless they are genuinely relevant.
- Answer the question directly and completely.
- If the information you found has nuance (e.g., different hours on different days), include the relevant details.

## 5. Tone & Style
- Match the tone of the original email. If it's casual, be casual. If it's formal, be formal.
- Keep the reply short and to the point — don't over-explain."""


def _claude(prompt: str) -> str:
    """Call the Anthropic API and return the text response."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def _search(query: str, max_results: int = 5) -> str:
    """Run a DuckDuckGo search and return formatted results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"• {r.get('title', '')}\n  {r.get('body', '')}")
        return "\n\n".join(lines)
    except Exception as exc:
        return f"Search error: {exc}"


class AIDraftGenerator:
    """Generates email drafts using the claude CLI with optional web search."""

    def generate_draft(self, email_data: Dict) -> Dict:
        sender  = email_data.get("sender",  "")
        subject = email_data.get("subject", "No Subject")
        body    = email_data.get("body",    "").strip()
        snippet = email_data.get("snippet", "")
        email_text = body or snippet

        # ── Step 1: decide whether web search is needed ────────────────────
        search_prompt = (
            "You are analyzing an incoming email to decide if a web search is needed "
            "to answer it accurately.\n\n"
            f"From: {sender}\nSubject: {subject}\n\n{email_text}\n\n"
            "If this email asks about real-world facts (business hours, prices, "
            "locations, events, availability, etc.) that require a web search, "
            "output ONLY valid JSON: {\"needs_search\": true, \"query\": \"<search query>\"}\n"
            "Otherwise output ONLY: {\"needs_search\": false}"
        )
        search_decision_raw = _claude(search_prompt)

        # extract JSON even if claude wraps it in markdown
        search_info = {"needs_search": False}
        try:
            # strip possible ```json ... ``` fences
            cleaned = search_decision_raw.strip().strip("`").strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            search_info = json.loads(cleaned)
        except Exception:
            pass

        # ── Step 2: run the search if needed ──────────────────────────────
        search_context = ""
        if search_info.get("needs_search"):
            query = search_info.get("query", subject)
            print(f"  [AI] Searching: {query}")
            results = _search(query)
            search_context = (
                f"\n\nWeb search results for \"{query}\":\n{results}\n"
                "Use only the relevant facts from these results in your reply."
            )

        # ── Step 3: detect the language of the incoming email ─────────────
        lang = _claude(
            f"What language is this email written in? Reply with ONLY the language name in English "
            f"(e.g. 'Hebrew', 'English', 'Arabic'). No other text.\n\n{email_text}"
        ).strip()
        print(f"  [AI] Detected language: {lang}")

        # ── Step 4: generate the draft ─────────────────────────────────────
        draft_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "---\n"
            "Incoming email:\n"
            f"From: {sender}\nSubject: {subject}\n\n{email_text}"
            f"{search_context}\n\n"
            "---\n"
            f"IMPORTANT: The email above is written in {lang}. "
            f"You MUST write your reply in {lang} only. Do not use any other language.\n\n"
            "Write ONLY the email body. No subject line, no metadata."
        )
        draft_body = _claude(draft_prompt)

        return {
            "draft_subject":    f"Re: {subject}",
            "draft_body":       draft_body,
            "original_sender":  sender,
            "original_subject": subject,
            "template_used":    "claude-cli",
            "email_id":         email_data.get("id", ""),
            "snippet":          snippet,
        }
