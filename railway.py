from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import subprocess
import sys

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        print("✅ Healthcheck OK")
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"✅ Healthcheck server running on port {port}")
    server.serve_forever()

def run_bot():
    print("🚀 Starting bot...")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    # راه‌اندازی healthcheck server در thread جدا
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # اجرای ربات اصلی
    run_bot()
