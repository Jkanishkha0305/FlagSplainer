#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error


def http_post_json(url: str, token: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Kafka-Lenses-Token", token)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    base = os.environ["LENSES_API_HTTP_URL"].rstrip("/")
    port = os.environ.get("LENSES_API_HTTP_PORT", "8080")
    token = os.environ["LENSES_API_KEY"]
    env = os.environ.get("LENSES_ENV", "financial-data")

    # Try common SQL endpoints (v2, v1, legacy)
    base_url = f"{base}:{port}"
    prefixes = [
        "",  # root
        "/api",
        "/lenses/api",
        "/ui/api",
    ]
    tails = [
        "/v2/sql/execute",
        "/v1/sql/execute",
        "/sql/execute",
    ]
    endpoints = [f"{base_url}{p}{t}" for p in prefixes for t in tails]

    payload = {
        "environment": env,
        "sql": "SELECT transaction_id, amount, category, customer_id FROM `credit-card-transactions` LIMIT 3",
    }

    last_err = None
    for url in endpoints:
        try:
            result = http_post_json(url, token, payload)
            print(json.dumps(result, indent=2))
            return
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            last_err = f"HTTP {e.code} {url}: {body}"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"

    raise SystemExit(f"Failed to execute SQL via Lenses API. Last error: {last_err}")


if __name__ == "__main__":
    main()


