#!/usr/bin/env python3
import base64
import html
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

PORT = int(os.environ.get("DASHBOARD_PORT", "8090"))
RPC_HOST = os.environ.get("FRACTAL_RPC_HOST", "fractald")
RPC_PORT = int(os.environ.get("FRACTAL_RPC_PORT", "8332"))
RPC_USER = os.environ.get("FRACTAL_RPC_USER", "fractalrpc")
RPC_PASSWORD = os.environ.get("FRACTAL_RPC_PASSWORD", "")
DATA_DIR = Path(os.environ.get("FRACTAL_DATA_DIR", "/fractal"))


def rpc_call(method, params=None):
    payload = json.dumps({"jsonrpc": "1.0", "id": "frbtc-dashboard", "method": method, "params": params or []}).encode()
    auth = base64.b64encode(f"{RPC_USER}:{RPC_PASSWORD}".encode()).decode()
    request = Request(
        f"http://{RPC_HOST}:{RPC_PORT}",
        data=payload,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
    )
    with urlopen(request, timeout=4) as response:
        body = json.load(response)
    if body.get("error"):
        raise RuntimeError(str(body["error"]))
    return body.get("result")


def directory_size(path):
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def format_bytes(value):
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return "—"


def status_snapshot():
    chain = rpc_call("getblockchaininfo")
    network = rpc_call("getnetworkinfo")
    return {
        "blocks": int(chain.get("blocks", 0)),
        "headers": int(chain.get("headers", 0)),
        "progress": float(chain.get("verificationprogress", 0)),
        "pruned": bool(chain.get("pruned", False)),
        "peers": int(network.get("connections", 0)),
        "version": str(network.get("subversion", "unknown")),
        "disk": directory_size(DATA_DIR),
    }


def render():
    try:
        status = status_snapshot()
        online = True
        error = ""
    except Exception:
        status = {"blocks": 0, "headers": 0, "progress": 0, "pruned": True, "peers": 0, "version": "unavailable", "disk": directory_size(DATA_DIR)}
        online = False
        error = "Fractald RPC is not available yet. The node may still be starting."
    syncing = online and (status["headers"] > status["blocks"] or status["progress"] < 0.9999)
    state = "Synchronizing" if syncing else ("Online" if online else "Starting")
    state_class = "warn" if syncing else ("up" if online else "down")
    notice = f'<div class="notice">{html.escape(error)}</div>' if error else ""
    updated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    rows = [
        ("Status", state),
        ("Block height", f'{status["blocks"]:,}'),
        ("Header height", f'{status["headers"]:,}'),
        ("Sync progress", f'{status["progress"] * 100:.4f}%'),
        ("Peers", str(status["peers"])),
        ("Pruned", "Yes" if status["pruned"] else "No"),
        ("Data stored", format_bytes(status["disk"])),
        ("Version", status["version"]),
    ]
    row_html = "".join(
        f'<div class="row"><span>{html.escape(label)}</span><strong class="{state_class if label == "Status" else ""}">{html.escape(value)}</strong></div>'
        for label, value in rows
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="30"><title>Fractal Bitcoin Node</title><style>
:root{{color-scheme:dark;--bg:#0b0e13;--panel:#151a22;--line:#293142;--text:#f5f7fa;--muted:#9aa4b2;--good:#38c979;--warn:#e6ad3d;--bad:#ef5e68;--accent:#ff9f43}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif}}main{{width:min(680px,calc(100% - 32px));margin:42px auto}}header{{display:flex;align-items:center;gap:14px;margin-bottom:24px}}.mark{{width:42px;height:42px;border:3px solid var(--accent);border-radius:12px;transform:rotate(45deg)}}h1{{font-size:27px;margin:0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:8px 22px}}.row{{display:flex;justify-content:space-between;gap:20px;padding:15px 0}}.row+.row{{border-top:1px solid var(--line)}}.up{{color:var(--good)}}.warn{{color:var(--warn)}}.down{{color:var(--bad)}}.notice{{background:#392d13;color:#f4cd78;padding:12px;border-radius:9px;margin-bottom:18px}}footer{{color:var(--muted);font-size:12px;text-align:center;margin-top:18px}}</style></head><body><main><header><div class="mark"></div><h1>Fractal Bitcoin Node</h1></header>{notice}<section class="card">{row_html}</section><footer>Last updated {html.escape(updated)} · refreshes every 30 seconds</footer></main></body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = render()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"Fractal dashboard listening on 0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
