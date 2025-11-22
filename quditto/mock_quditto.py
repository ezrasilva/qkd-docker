# mock_quditto.py (Versão Estabilizada)
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, secrets, time, hashlib

# Configuração
KEY_TTL_SECONDS = 60

class Handler(BaseHTTPRequestHandler):
    
    def _get_current_key(self):
        # Usa o timestamp inteiro dividido pelo TTL para criar "janelas" de tempo.
        # Ex: Se TTL=60, todo timestamp entre 1200 e 1259 gera o mesmo 'time_window'.
        time_window = int(time.time() / KEY_TTL_SECONDS)
        
        # Gera uma chave determinística para essa janela de tempo
        # Isso garante que Host A e Host B recebam a MESMA chave se chamarem dentro do mesmo minuto.
        seed = f"super-secret-seed-{time_window}".encode()
        
        # Deriva as chaves usando SHA256 para garantir entropia consistente
        full_hash = hashlib.sha256(seed).hexdigest()
        
        key_id = full_hash[:16]       # Primeiros 16 chars como ID
        enc_key = full_hash[16:]      # Restante como chave (simulada)
        
        # Calcula TTL restante para o fim da janela atual
        next_window = (time_window + 1) * KEY_TTL_SECONDS
        remaining_ttl = next_window - time.time()

        return {
            "key_id": key_id,
            "enc_key_hex": enc_key,
            "ttl": max(0, remaining_ttl) # Evita TTL negativo
        }

    def do_GET(self):
        if self.path == "/keys/next":
            resp = self._get_current_key()
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())
            print(f"[Quditto] Servindo chave ID {resp['key_id']} (TTL={resp['ttl']:.1f}s)")
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Mock Quditto (Sincronizado) rodando na porta 8000...")
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()