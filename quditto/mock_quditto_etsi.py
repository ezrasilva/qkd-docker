# mock_quditto_etsi.py
from fastapi import FastAPI, HTTPException
import time
import hashlib

app = FastAPI()

# Configuração
KEY_TTL_SECONDS = 60
KEY_SIZE_BYTES = 32 # 256 bits

def _generate_time_based_key():
    """
    Gera uma chave determinística baseada no minuto atual.
    Assim, Alice e Bob recebem a mesma chave se pedirem ao mesmo tempo.
    """
    time_window = int(time.time() / KEY_TTL_SECONDS)
    seed = f"etsi-secret-seed-{time_window}".encode()
    full_hash = hashlib.sha256(seed).hexdigest()
    
    return {
        "key_id": full_hash[:16],       # ID da chave
        "key": full_hash[16:],          # Chave hex (simulando chave quântica)
        "ttl": KEY_TTL_SECONDS - (time.time() % KEY_TTL_SECONDS)
    }

# --- Endpoints ETSI QKD 014 (Inspirado no http_receptor.py) ---

# Endpoint para solicitar uma NOVA chave (usado por Alice e Bob nesta PoC)
@app.get("/api/v1/keys/{slave_SAE_ID}/enc_keys")
def get_enc_key(slave_SAE_ID: str, size: str = "256"):
    # Na PoC, ignoramos o slave_SAE_ID para a geração da chave,
    # confiando apenas no tempo para sincronizar os dois lados.
    data = _generate_time_based_key()
    
    # Formato de resposta padrão ETSI
    return {
        "keys": [
            {
                "key_ID": data["key_id"],
                "key": data["key"]
            }
        ],
        "ttl": data["ttl"]
    }

# Endpoint para buscar uma chave por ID (Decryption keys)
# O código do Quditto real tem esse endpoint. Vamos mockar também.
@app.get("/api/v1/keys/{master_SAE_ID}/dec_keys")
def get_dec_key(master_SAE_ID: str, key_ID: str):
    # Verifica se o ID pedido bate com a chave atual do tempo
    current = _generate_time_based_key()
    
    if key_ID == current["key_id"]:
        return {
            "keys": [
                {
                    "key_ID": current["key_id"],
                    "key": current["key"]
                }
            ]
        }
    else:
        # Num sistema real, buscaria no DB. Aqui, retorna erro se expirou.
        raise HTTPException(status_code=404, detail="Key not found or expired")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)