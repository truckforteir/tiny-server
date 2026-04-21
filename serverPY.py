from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen
from urllib.parse import urlencode, parse_qs, urlparse
import json

EMPRESAS = {
    "TruckPontoCom1": "e4967a5c57fcd48fe5a69c6fa8c8d9d62d3e014f",
    "TruckPontoCom2": "a53f96644e3cf95542c5442a4722eaaba931bf64",
    "TruckPontoCom3": "a7bf6e57c6d6797e83323fa199cab56076b56a647718f0ed60eae803857125a9",
    "TruckPontoCom4": "53b8b214a53c07efb908ea9572784312383ec2e60e807eecfc4b18173419c223",
}

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        empresa = params.get("empresa", [""])[0]
        endpoint = params.get("endpoint", [""])[0]
        situacao = params.get("situacao", [""])[0]
        pesquisa = params.get("pesquisa", [""])[0]

        if not empresa or empresa not in EMPRESAS:
            self.responder({"erro": "Empresa inválida"}, 400)
            return

        token = EMPRESAS[empresa]
        p = {"token": token, "formato": "JSON"}
        if situacao: p["situacao"] = situacao
        if pesquisa: p["pesquisa"] = pesquisa

        url = f"https://api.tiny.com.br/api2/{endpoint}?{urlencode(p)}"
        try:
            with urlopen(url, timeout=15) as r:
                data = json.loads(r.read().decode())
            self.responder(data)
        except Exception as e:
            self.responder({"erro": str(e)}, 500)

    def responder(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args): pass

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print(f"Servidor rodando na porta {port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
