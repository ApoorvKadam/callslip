"""Calls to Claude, each recorded in the `llm_calls` ledger with tokens and estimated cost.

The SDK retries transient failures (connection errors, 429, 5xx) on its own. The whole call,
retries included, is bounded by the caller's timeout, so it can never run past a deadline.
"""

import asyncio
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

from anthropic import AsyncAnthropic
from anthropic.types import Message
from psycopg_pool import AsyncConnectionPool

# USD per million tokens: input, output, cache write (5-minute TTL), cache read.
PRICES: dict[str, tuple[float, float, float, float]] = {
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 0.20),
    "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.01),
}


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    cost_usd: float
    ms: int


def estimate_cost(model: str, usage: Any) -> float:
    price_in, price_out, price_write, price_read = PRICES[model]
    cost = (
        usage.input_tokens * price_in
        + usage.output_tokens * price_out
        + (usage.cache_creation_input_tokens or 0) * price_write
        + (usage.cache_read_input_tokens or 0) * price_read
    ) / 1_000_000
    return round(cost, 6)


class LLM:
    def __init__(self, client: AsyncAnthropic, pool: AsyncConnectionPool, model: str, effort: str):
        if model not in PRICES:
            raise ValueError(f"no price for model {model}; add it to PRICES")
        self.client = client
        self.pool = pool
        self.model = model
        self.effort = effort

    async def create(
        self,
        *,
        run_id: UUID | None,
        purpose: str,
        system: list[dict],
        messages: list[dict],
        timeout_s: float,
        max_tokens: int = 4000,
        tools: list[dict] | None = None,
        tool_choice: dict | None = None,
    ) -> tuple[Message, Usage]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
            "output_config": {"effort": self.effort},
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice

        started = time.monotonic()
        message = await asyncio.wait_for(
            self.client.with_options(timeout=timeout_s).messages.create(**kwargs), timeout_s
        )
        ms = int((time.monotonic() - started) * 1000)

        u = message.usage
        usage = Usage(
            u.input_tokens,
            u.output_tokens,
            u.cache_creation_input_tokens or 0,
            u.cache_read_input_tokens or 0,
            estimate_cost(self.model, u),
            ms,
        )
        async with self.pool.connection() as conn:
            await conn.execute(
                "INSERT INTO llm_calls (run_id, purpose, model, input_tokens, output_tokens,"
                " cache_creation_tokens, cache_read_tokens, cost_usd, ms, stop_reason, request_id)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    run_id,
                    purpose,
                    self.model,
                    usage.input_tokens,
                    usage.output_tokens,
                    usage.cache_creation_tokens,
                    usage.cache_read_tokens,
                    Decimal(str(usage.cost_usd)),
                    ms,
                    message.stop_reason,
                    getattr(message, "_request_id", None),
                ),
            )
        return message, usage
