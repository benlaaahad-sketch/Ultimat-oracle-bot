from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import sys
import time

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        print(f"✅ Healthcheck received at {time.strftime('%H:%M:%S')}")
    
    def log_message(self, format, *args):
        pass  # خاموش کردن لاگ‌های اضافی

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"✅ Healthcheck server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_health_server()
