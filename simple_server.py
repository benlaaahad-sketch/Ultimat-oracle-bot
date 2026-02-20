#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys
import subprocess
import threading

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"✅ Health server running on port {port}")
    server.serve_forever()

# راه‌اندازی سرور healthcheck
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# اجرای ربات اصلی
print("🚀 Starting main bot...")
subprocess.run([sys.executable, "main.py"])
