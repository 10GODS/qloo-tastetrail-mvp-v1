"""Dependency-free local web app for the TasteTrail MVP."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tastetrail.core import build_plan
from tastetrail.qloo import QlooClient, QlooError


HTML = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TasteTrail Jaipur</title><style>body{font:16px system-ui;max-width:760px;margin:40px auto;padding:0 18px;background:#fffaf3;color:#24211d}label{display:block;margin:12px 0 4px;font-weight:600}input,textarea,button{width:100%;padding:10px;border:1px solid #c9bca8;border-radius:8px;box-sizing:border-box}button{margin-top:16px;background:#2d5a4a;color:white;cursor:pointer}pre{white-space:pre-wrap;background:#f2eadf;padding:14px;border-radius:8px}</style></head>
<body><h1>TasteTrail Jaipur</h1><p>Constraint-aware recommendations grounded in Qloo cultural intelligence.</p>
<label>Location</label><input id="location" value="Jaipur"><label>Interests (comma separated)</label><input id="interests" value="heritage, vegetarian food"><label>Budget</label><input id="budget" value="moderate"><label>Time window</label><input id="time_window" value="one day"><label>Constraints (comma separated)</label><input id="constraints" value="walkable"><button onclick="plan()">Build my plan</button><pre id="out">Enter your preferences, then build a plan.</pre>
<script>async function plan(){const csv=id=>document.getElementById(id).value.split(',').map(x=>x.trim()).filter(Boolean);const body={location:document.getElementById('location').value,interests:csv('interests'),budget:document.getElementById('budget').value,time_window:document.getElementById('time_window').value,constraints:csv('constraints')};const r=await fetch('/api/plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: object, content_type: str = "application/json") -> None:
        body = payload if isinstance(payload, bytes) else (payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode("utf-8"))
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"ok": True, "qloo_key_configured": bool(__import__("os").environ.get("QLOO_API_KEY"))})
            return
        self._send(200, HTML, "text/html; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/plan":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = build_plan(payload, QlooClient())
            self._send(200, result)
        except (ValueError, QlooError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})


if __name__ == "__main__":
    print("TasteTrail listening at http://127.0.0.1:8765")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()

