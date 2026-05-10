"""OpenAI-compatible LLM provider with a mock fallback."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from dotenv import load_dotenv


class LLMProvider(Protocol):
    """Text generation interface used by the research agent."""

    provider_name: str

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        ...


@dataclass
class MockLLMProvider:
    """Deterministic provider that keeps the project runnable without API keys."""

    provider_name: str = "mock"

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        snippet = prompt.strip().replace("\n", " ")[:500]
        return (
            "Mock LLM response: I analyzed the available experiment context and generated a rule-based answer. "
            f"Prompt excerpt: {snippet}"
        )


@dataclass
class OpenAICompatibleProvider:
    """Minimal OpenAI-compatible chat completion client using urllib."""

    api_key: str
    base_url: str
    model: str
    provider_name: str = "openai-compatible"
    timeout: int = 60

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                    or "You are a research assistant for 3D plant point cloud segmentation experiments.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            return MockLLMProvider().generate(f"Provider request failed: {exc}\n\n{prompt}", system_prompt)

        try:
            return str(body["choices"][0]["message"]["content"])
        except Exception:
            return MockLLMProvider().generate(f"Unexpected provider response: {body}\n\n{prompt}", system_prompt)


def get_llm_provider() -> LLMProvider:
    """Create an LLM provider from environment variables."""
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    api_key = os.getenv("LLM_API_KEY", "")
    if provider == "mock" or not api_key:
        return MockLLMProvider()
    return OpenAICompatibleProvider(
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    )
