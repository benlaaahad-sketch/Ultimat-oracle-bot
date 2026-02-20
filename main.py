#!/usr/bin/env python3
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, *args):
        pass

def run_health():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"✅ Health server on port {port}")
    server.serve_forever()

thread = threading.Thread(target=run_health, daemon=True)
thread.start()

# ایمپورت ربات اصلی
from bot.ultimate_bot import UltimateBot
from database.models import init_database

init_database()
bot = UltimateBot()
bot.run()
