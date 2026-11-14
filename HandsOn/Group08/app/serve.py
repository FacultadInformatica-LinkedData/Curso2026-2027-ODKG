"""Serves the Barcelona Heat Relief application and forwards its SPARQL queries to GraphDB.

The browser talks to this server only: the files of the application are served from this
folder and every request to /sparql is forwarded to the GraphDB repository, so GraphDB does
not need any CORS setting.

Usage (from this folder): python serve.py [--port 8080] [--graphdb URL] [--no-browser]
GraphDB Desktop must be running, with the repository barcelona-heat-relief loaded.
Only the Python standard library is used.
"""
import argparse
import http.server
import urllib.error
import urllib.request
import webbrowser
from functools import partial
from pathlib import Path

DEFAULT_GRAPHDB = "http://localhost:7200/repositories/barcelona-heat-relief"


class Handler(http.server.SimpleHTTPRequestHandler):
    graphdb = DEFAULT_GRAPHDB
    # Explicit types: on Windows the registry can map .js to text/plain, which browsers
    # refuse for JavaScript modules.
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html",
        ".js": "text/javascript",
        ".css": "text/css",
        ".svg": "image/svg+xml",
        ".json": "application/json",
    }

    def do_GET(self):
        if self.path.split("?")[0] == "/sparql":
            self.forward(None)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/sparql":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        self.forward(self.rfile.read(length))

    def forward(self, body):
        query_string = self.path.partition("?")[2]
        url = self.graphdb + ("?" + query_string if query_string else "")
        headers = {"Accept": self.headers.get("Accept", "application/sparql-results+json")}
        if body is not None:
            headers["Content-Type"] = self.headers.get("Content-Type", "application/x-www-form-urlencoded")
        request = urllib.request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                status = response.status
                content_type = response.headers.get("Content-Type", "application/sparql-results+json")
                data = response.read()
        except urllib.error.HTTPError as error:
            status, content_type, data = error.code, error.headers.get("Content-Type", "text/plain"), error.read()
        except (urllib.error.URLError, OSError) as error:
            status, content_type = 502, "text/plain; charset=utf-8"
            data = f"GraphDB is not reachable at {self.graphdb}: is GraphDB Desktop running? ({error})".encode()
            print(f"GraphDB not reachable at {self.graphdb}: {error}")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def end_headers(self):
        # Always serve the latest version of the files.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # no line per request


def main():
    parser = argparse.ArgumentParser(description="Serve the application and forward its SPARQL queries to GraphDB.")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--graphdb", default=DEFAULT_GRAPHDB, help="SPARQL endpoint of the GraphDB repository")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = parser.parse_args()
    Handler.graphdb = args.graphdb
    handler = partial(Handler, directory=str(Path(__file__).resolve().parent))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"Application: {url} (queries forwarded to {args.graphdb}). Stop with Ctrl+C.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
