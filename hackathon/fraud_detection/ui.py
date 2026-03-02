"""
Minimal Starlette UI for interacting with the fraud detection workflow.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.routing import Route

from .runner import run_fraud_detection
from .state import FraudState

latest_result: Optional[FraudState] = None


def _build_alert_rows(state: FraudState) -> str:
    if not state["fraud_alerts"]:
        return "<p>No alerts generated.</p>"

    rows = []
    for index, alert in enumerate(
        sorted(state["fraud_alerts"], key=lambda item: item["risk_score"], reverse=True),
        1,
    ):
        evidence_items = "<br>".join(
            f"<strong>{key}:</strong> {value}" for key, value in alert["evidence"].items()
        )
        rows.append(
            f"""
            <div class="alert-card">
              <div class="alert-header">
                <span class="alert-index">#{index}</span>
                <span class="alert-risk">Risk {alert['risk_score']}/10</span>
              </div>
              <div class="alert-body">
                <p><strong>Customer:</strong> {alert['customer_id']}</p>
                <p><strong>Pattern:</strong> {alert['pattern']}</p>
                <p><strong>Description:</strong> {alert['description']}</p>
                <p><strong>Recommendation:</strong> {alert['recommendation']}</p>
                <details>
                  <summary>Evidence</summary>
                  <p>{evidence_items}</p>
                </details>
              </div>
            </div>
            """
        )
    return "\n".join(rows)


def _render_homepage(state: Optional[FraudState]) -> str:
    summary_block = (
        f"<pre>{state['summary']}</pre>" if state and state.get("summary") else "<p>No results yet.</p>"
    )
    alerts_block = _build_alert_rows(state) if state else "<p>No alerts generated.</p>"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>Fraud Detection Dashboard</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 2rem;
          background: #f5f7fb;
        }}
        .container {{
          max-width: 960px;
          margin: 0 auto;
        }}
        header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }}
        h1 {{
          margin: 0;
        }}
        form button {{
          background: #2563eb;
          border: none;
          color: white;
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          border-radius: 0.5rem;
          cursor: pointer;
        }}
        form button:hover {{
          background: #1e3a8a;
        }}
        section {{
          background: white;
          border-radius: 0.75rem;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }}
        pre {{
          background: #0f172a;
          color: #f8fafc;
          padding: 1rem;
          border-radius: 0.5rem;
          overflow-x: auto;
          white-space: pre-wrap;
        }}
        .alert-card {{
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
          padding: 1rem 1.25rem;
          margin-bottom: 1rem;
          background: #f8fafc;
        }}
        .alert-header {{
          display: flex;
          justify-content: space-between;
          margin-bottom: 0.5rem;
          font-weight: 600;
        }}
        .alert-index {{
          color: #0f172a;
        }}
        .alert-risk {{
          color: #b91c1c;
        }}
        details summary {{
          cursor: pointer;
          font-weight: 600;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <header>
          <h1>Fraud Detection Dashboard</h1>
          <form method="post" action="/run">
            <button type="submit">Run Detection</button>
          </form>
        </header>

        <section>
          <h2>Summary</h2>
          {summary_block}
        </section>

        <section>
          <h2>Alerts</h2>
          {alerts_block}
        </section>
      </div>
    </body>
    </html>
    """


async def homepage(_: Request) -> Response:
    """Render the dashboard with the latest results."""
    return HTMLResponse(_render_homepage(latest_result))


async def run_detection(_: Request) -> Response:
    """Trigger the fraud detection workflow and redirect back to the dashboard."""
    global latest_result
    latest_result = await asyncio.to_thread(run_fraud_detection)
    return RedirectResponse(url="/", status_code=303)


app = Starlette(debug=False, routes=[Route("/", homepage, methods=["GET"]), Route("/run", run_detection, methods=["POST"])])

