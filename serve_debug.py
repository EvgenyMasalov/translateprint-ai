import http.server
import socketserver
import os
import sys

PORT = 8081 # НОВЫЙ ПОРТ ДЛЯ ПРОВЕРКИ
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class DebugHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('X-Debug-Mode', 'Active')
        super().end_headers()

    def guess_type(self, path):
        print(f"[DEBUG] Guessing type for {path}")
        if path.endswith('.js'):
            return 'application/javascript'
        return super().guess_type(path)

if __name__ == "__main__":
    os.chdir(ROOT_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    print(f"--- Debug Server on {PORT} ---")
    with socketserver.TCPServer(("127.0.0.1", PORT), DebugHandler) as httpd:
        httpd.serve_forever()
