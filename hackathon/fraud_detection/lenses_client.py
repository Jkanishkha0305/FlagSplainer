"""
Standalone Lenses WebSocket client for fraud detection.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

try:
    import websockets
except ImportError:
    websockets = None

from ..config import Config


class LensesWebSocketClient:
    """WebSocket client for querying Kafka topics via Lenses SQL."""

    def __init__(self, base_url: str, bearer_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {bearer_token}"}

    async def execute_sql(
        self, environment: str, sql: str
    ) -> List[Dict[str, Any]]:
        """Execute SQL query via Lenses WebSocket API."""
        endpoint = f"/api/v1/environments/{environment}/proxy/api/ws/v2/sql/execute"
        uri = f"{self.base_url}{endpoint}"

        try:
            # Use extra_headers (works with websockets 13.x and most versions)
            async with websockets.connect(
                uri=uri, extra_headers=self.headers
            ) as ws:
                return await self._process_websocket(ws, sql)

        except Exception as exc:
            print(f"  ✗ WebSocket error: {exc}")
            raise exc

    async def _process_websocket(self, ws, sql: str) -> List[Dict[str, Any]]:
        """Process WebSocket messages."""
        try:
            records = []
            await ws.send(json.dumps({"sql": sql}))

            while True:
                response = await ws.recv()
                data = json.loads(response)
                message_type = data["type"].upper()

                if message_type == "RECORD":
                    data_payload = data.get("data")
                    if data_payload:
                        records.append(data_payload)

                elif message_type == "END":
                    print(f"  ✓ SQL query complete: {len(records)} records")
                    return records

                elif message_type == "ERROR":
                    error_msg = data.get("message", "Unknown error")
                    print(f"  ✗ SQL query error: {error_msg}")
                    return records

        except Exception as exc:
            print(f"  ✗ Error processing WebSocket messages: {exc}")
            raise exc


def create_lenses_client() -> LensesWebSocketClient | None:
    """Create a Lenses WebSocket client with current config."""
    if websockets is None:
        print("  ⚠️  websockets library not available")
        return None

    if not Config.LENSES_API_KEY:
        print("  ⚠️  LENSES_API_KEY not configured")
        return None

    base_url = f"{Config.LENSES_API_WEBSOCKET_URL}:{Config.LENSES_API_WEBSOCKET_PORT}"
    return LensesWebSocketClient(base_url, Config.LENSES_API_KEY)
