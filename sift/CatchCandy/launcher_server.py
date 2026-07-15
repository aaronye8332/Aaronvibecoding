import os
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


class LauncherHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/run-game':
            try:
                cwd = os.path.dirname(os.path.abspath(__file__))
                subprocess.Popen(
                    ['python3', 'game.py'],
                    cwd=cwd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"started"}')
            except Exception as exc:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"status":"error","message":"{exc}"}}'.encode())
            return

        return super().do_GET()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = ThreadingHTTPServer(('127.0.0.1', 8000), LauncherHandler)
    print('Launcher server running at http://127.0.0.1:8000')
    server.serve_forever()
