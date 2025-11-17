# mock_quditto.py (Stateful com Cache)
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, secrets, time

# --- Cache Global da Chave ---
KEY_CACHE = {
    "key_id": None,
    "enc_key_hex": None,
    "auth_key_hex": None,
    "generation_time": 0
}
KEY_TTL_SECONDS = 60  # A chave é válida por 60 segundos
# ---------------------------

class Handler(BaseHTTPRequestHandler):
    
    def _get_key(self):
        """
        Verifica o cache. Se a chave estiver expirada ou não existir, 
        gera uma nova. Retorna a chave atual.
        """
        global KEY_CACHE
        now = time.time()
        
        # Verifica se a chave expirou ou se é a primeira execução
        if (now - KEY_CACHE["generation_time"]) > KEY_TTL_SECONDS or KEY_CACHE["key_id"] is None:
            print(f"[Quditto] Gerando nova chave (TTL={KEY_TTL_SECONDS}s)...")
            KEY_CACHE = {
                "key_id": secrets.token_hex(8),
                "enc_key_hex": secrets.token_hex(32),
                "auth_key_hex": secrets.token_hex(32), # Para o Passo 6 (XFRM)
                "generation_time": now
            }
        else:
            print(f"[Quditto] Servindo chave do cache: {KEY_CACHE['key_id']}")

        # Calcula o TTL restante
        remaining_ttl = KEY_TTL_SECONDS - int(now - KEY_CACHE["generation_time"])
        
        return {
            "key_id": KEY_CACHE["key_id"],
            "enc_key_hex": KEY_CACHE["enc_key_hex"],
            "auth_key_hex": KEY_CACHE["auth_key_hex"],
            "ttl": remaining_ttl
        }

    def do_GET(self):
        if self.path == "/keys/next":
            resp = self._get_key()
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Mock Quditto (Stateful) rodando na porta 8000...")
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()