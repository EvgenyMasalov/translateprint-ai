import http.server
import socketserver
import os
import mimetypes

PORT = 8080
DIRECTORY = "."

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Перехватываем GET запросы для JS и CSS
        if self.path.endswith('.js') or self.path.endswith('.css'):
            path = self.path.split('?')[0].split('#')[0]
            full_path = os.path.join(DIRECTORY, path.lstrip('/'))
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                else:
                    self.send_header('Content-Type', 'text/css')
                
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                return
        
        return super().do_GET()

if __name__ == "__main__":
    # Явно сбрасываем mimetypes и добавляем типы
    mimetypes.init()
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    
    # Пытаемся заставить Python игнорировать реестр
    if hasattr(mimetypes, 'knownfiles'):
        mimetypes.knownfiles = [] # Очищаем список файлов с типами (включая реестр на Windows)

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
