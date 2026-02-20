from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # خاموش کردن لاگ‌های اضافی

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()

# راه‌اندازی سرور healthcheck در یه thread جدا
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

print("✅ Healthcheck server running on port 8080")
