#!/usr/bin/env python3
import http.server, socketserver, os, glob, json, re
from datetime import datetime

OUTPUT_DIR = "/root/tokfm-vosk/output"
PORT = 20104

def last_lines(n=10):
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "tokfm_*.txt")))
    if not files: return []
    lines = []
    with open(files[-1], "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            m = re.match(r'^\[(.+?)\]\s+(.+)', line)
            if m: lines.append((m.group(1), m.group(2)))
    return lines[-n:]

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        lines = last_lines()
        now = datetime.now().strftime("%H:%M:%S")
        rows = "".join(
            f'<div class="line"><span class="ts">{ts}</span>{txt}</div>'
            for ts, txt in lines
        )
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="6">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TOK FM LIVE</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000;color:#0f0;font:16px/1.6 'Courier New',monospace;padding:20px}}
h1{{font-size:14px;color:#333;margin-bottom:10px}}
#log{{white-space:pre-wrap;word-break:break-word;height:calc(100vh - 100px);overflow:hidden;padding:10px}}
.line{{padding:2px 0;border-bottom:1px solid #1a1a1a}}
.ts{{color:#555;margin-right:10px}}
.status{{position:fixed;top:10px;right:20px;font-size:11px;padding:4px 10px;border-radius:3px;z-index:99;background:#030;color:#0f0}}
.info{{color:#555;font-size:12px;margin-bottom:8px}}
</style>
</head>
<body>
<h1>📻 TOK FM — transkrypcja LIVE (Mikrus)</h1>
<div class="status">● LIVE</div>
<div class="info">auto-refresh 6s | {len(lines)} wierszy | {now}</div>
<div id="log">{rows}</div>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())
    def log_message(self, *a): pass

class TS(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    TS(("0.0.0.0", PORT), H).serve_forever()
