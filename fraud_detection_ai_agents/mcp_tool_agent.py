#!/usr/bin/env python3
"""
Minimal LLM agent that calls a Lenses MCP tool (list topics) over HTTP
and generates a short natural-language summary.

Environment variables required:
  - LENSES_URL          e.g. https://your-lenses-host
  - LENSES_AGENT_KEY    agent key/token for MCP agent
  - LENSES_ENV          e.g. financial-data
"""

import os
import argparse
import json
import ssl
import urllib.request
import urllib.error
from typing import Any, Dict, List

from llm_narrative_agent import LLMNarrativeAgent


class MCPLLMToolAgent:
    """
    Small helper that fetches Kafka topics via Lenses MCP HTTP API
    and asks an LLM to summarize them briefly.
    """

    def __init__(self) -> None:
        # Primary vars used by this script
        self.lenses_url = os.environ.get("LENSES_URL", "").rstrip("/")
        self.agent_key = os.environ.get("LENSES_AGENT_KEY", "")
        self.environment = os.environ.get("LENSES_ENV", "")

        # Back-compat with common Lenses .env styles
        if not self.lenses_url:
            base = os.environ.get("LENSES_API_HTTP_URL", "").rstrip("/")
            port = os.environ.get("LENSES_API_HTTP_PORT", "")
            if base:
                if port:
                    self.lenses_url = f"{base}:{port}"
                else:
                    self.lenses_url = base
                self.lenses_url = self.lenses_url.rstrip("/")

        if not self.agent_key:
            self.agent_key = os.environ.get("LENSES_API_KEY", "")
        self.llm = LLMNarrativeAgent()
        self.force_mock = False

    def _build_request(self, path: str) -> urllib.request.Request:
        if not self.lenses_url:
            raise RuntimeError("LENSES_URL is not set")
        url = f"{self.lenses_url}{path}"
        req = urllib.request.Request(url)
        if self.agent_key:
            req.add_header("Authorization", f"Bearer {self.agent_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        return req

    def _http_get_json(self, req: urllib.request.Request) -> Any:
        # Create permissive SSL context to avoid local cert issues (user can harden later)
        context = ssl.create_default_context()
        try:
            with urllib.request.urlopen(req, context=context, timeout=30) as resp:
                data = resp.read()
                if not data:
                    return None
                return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {e.code} calling {req.full_url}: {body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error calling {req.full_url}: {e}")

    def list_topics(self) -> List[Dict[str, Any]]:
        """
        Calls the Lenses topics listing endpoint for the target environment.
        This maps to the MCP capability "list_topics".
        """
        if self.force_mock or not (self.lenses_url and self.agent_key):
            # No credentials provided: return a small realistic mock set
            return [
                {"name": "credit-card-transactions", "partitions": 3, "messages": 7584401},
                {"name": "paypal-transactions", "partitions": 3, "messages": 3640550},
                {"name": "auto-loan-payments", "partitions": 3, "messages": 758440},
            ]
        # Common Lenses API paths; try v2 datasets first, then v2 topics.
        # Prefer the topics-rich endpoint when available.
        env_q = f"?environment={self.environment}" if self.environment else ""
        env_seg = f"/{self.environment}" if self.environment else ""
        # Try a variety of known Lenses API shapes across versions
        candidates = [
            # v2 generic
            f"/api/v2/topics{env_q}",
            f"/api/v2/kafka/topics{env_q}",
            f"/api/v2/kafka{env_seg}/topics",
            f"/api/v2/datasets{env_q}",
            "/api/v2/datasets?connections=kafka",
            # v1 fallbacks
            f"/api/v1/topics{env_q}",
            f"/api/v1/kafka/topics{env_q}",
            f"/api/v1/kafka{env_seg}/topics",
            f"/api/v1/datasets{env_q}",
            "/api/v1/datasets?connections=kafka",
            # legacy generic
            f"/api/topics{env_q}",
            f"/api/kafka/topics{env_q}",
            f"/api/kafka{env_seg}/topics",
            f"/api/datasets{env_q}",
            "/api/datasets?connections=kafka",
        ]

        last_error = None
        for path in candidates:
            req = self._build_request(path)
            try:
                payload = self._http_get_json(req)
                if not payload:
                    continue

                # Normalize to a list of topics with minimal keys.
                if isinstance(payload, dict) and "result" in payload and isinstance(payload["result"], list):
                    topics = payload["result"]
                elif isinstance(payload, dict) and "datasets" in payload and isinstance(payload["datasets"], dict):
                    topics = payload["datasets"].get("values", [])
                elif isinstance(payload, list):
                    topics = payload
                else:
                    topics = []

                normalized: List[Dict[str, Any]] = []
                for t in topics:
                    name = t.get("topicName") or t.get("name") or t.get("lrn") or "unknown"
                    partitions = t.get("partitions") if isinstance(t.get("partitions"), int) else (
                        len(t.get("messagesPerPartition", [])) if isinstance(t.get("messagesPerPartition", []), list) else None
                    )
                    messages = t.get("totalMessages") or t.get("records") or None
                    normalized.append({
                        "name": name,
                        "partitions": partitions,
                        "messages": messages,
                    })
                return normalized
            except Exception as err:  # noqa: BLE001
                last_error = err
                continue

        if last_error:
            raise last_error
        return []

    def summarize_topics(self, topics: List[Dict[str, Any]]) -> str:
        """
        Uses the existing LLMNarrativeAgent to produce a short summary.
        """
        # Reuse the Narrative generation with a simple prompt-style structure
        if not self.llm.enabled:
            # Fallback textual summary without LLM
            names = ", ".join(t.get("name", "unknown") for t in topics[:10])
            return f"LLM disabled. Found {len(topics)} topics. Examples: {names}"

        # Build a compact context
        context = {
            "topics": topics[:25],
            "count": len(topics),
            "environment": self.environment,
        }
        # Piggyback the existing API for narratives with a synthetic transaction
        narrative = self.llm.generate_fraud_narrative(
            transaction=context,  # type: ignore[arg-type]
            risk_score=0.0,
            risk_factors=["metadata"],
        )
        return narrative.narrative


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM agent that lists topics via Lenses MCP (or mock)")
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of calling MCP API")
    args = parser.parse_args()

    agent = MCPLLMToolAgent()
    agent.force_mock = bool(args.mock)

    topics = agent.list_topics()
    summary = agent.summarize_topics(topics)
    print(json.dumps({
        "environment": agent.environment,
        "topics_found": len(topics),
        "sample": topics[:5],
        "summary": summary,
    }, indent=2))


if __name__ == "__main__":
    main()


