"""Provider-agnostic LLM helper.

LLM_PROVIDER=mock       -> offline demo mode (no API key, deterministic output)
LLM_PROVIDER=openai     -> OpenAI or any OpenAI-compatible server (Ollama, vLLM, LM Studio)
LLM_PROVIDER=anthropic  -> Claude
"""
import json
import os
import re


def chat(system: str, user: str, mock: str = "", temperature: float = 0.3) -> str:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return mock
    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic()
        r = client.messages.create(
            model=os.getenv("LLM_MODEL", "claude-sonnet-5-5"),
            max_tokens=2500,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in r.content if b.type == "text")
    from openai import OpenAI

    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    )
    r = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return r.choices[0].message.content or ""


def extract_json(text: str, default=None):
    """Pull the first JSON object/array out of a model reply."""
    m = re.search(r"\{.*\}|\[.*\]", text or "", re.S)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return default


def strip_fences(text: str) -> str:
    m = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()
