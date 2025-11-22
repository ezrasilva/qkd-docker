import socket
import vici
import requests
import time
import sys
import os

# SAE_ID = Secure Application Entity ID (A identidade do Host na rede QKD)
MY_HOSTNAME = socket.gethostname() # Aqui ele chama o hostname do container
PEER_HOSTNAME = "host-b" if "host-a" in MY_HOSTNAME else "host-a" #O peer é o outro host

# aqui são os IDs IPsec usados na configuração do StrongSwan
MY_IPSEC_ID = "hostA" if "host-a" in MY_HOSTNAME else "hostB"
PEER_IPSEC_ID = "hostB" if "host-a" in MY_HOSTNAME else "hostA"

#Configuração do Quditto
QUDITTO_HOST = "quditto"
QUDITTO_PORT = 8000
# Socket do VICI do StrongSwan, pois é pelo VICI que injetamos as chaves
VICI_SOCKET = "/var/run/charon.vici"
CONN_NAME = "qkd-poc"

def fetch_key_etsi():
    """
    Consulta a API no formato ETSI QKD 014.
    GET /api/v1/keys/{slave_SAE_ID}/enc_keys
    """
    # Construindo a URL ETSI
    # Pedimos uma chave para encriptar comunicação destinada ao PEER_HOSTNAME
    url = f"http://{QUDITTO_HOST}:{QUDITTO_PORT}/api/v1/keys/{PEER_HOSTNAME}/enc_keys"
    
    try:
        # Parâmetro size é opcional no nosso mock, mas bom enviar por padrão
        r = requests.get(url, params={"size": "256"}, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        # O formato ETSI retorna uma lista de chaves. Pegamos a primeira.
        # Estrutura: { "keys": [ { "key_ID": "...", "key": "..." } ] }
        if "keys" in data and len(data["keys"]) > 0:
            return {
                "key_id": data["keys"][0]["key_ID"],
                "key_hex": data["keys"][0]["key"]
            }
        else:
            print("[Adapter] Resposta ETSI vazia ou inválida.")
            return None
            
    except Exception as e:
        print(f"[Adapter] Erro ao buscar chave ETSI: {e}", flush=True)
        return None

def inject_and_initiate(key_hex, key_id):
    s = None
    try:
        key_bytes = bytes.fromhex(key_hex)
        
        # Estrutura plana para o VICI
        shared_secret = {
            "type": "IKE",              
            "data": key_bytes,          
            "owners": [MY_IPSEC_ID, PEER_IPSEC_ID], 
            "id": f"qkd-key-{key_id}"   
        }

        s = socket.socket(socket.AF_UNIX)
        s.connect(VICI_SOCKET)
        v = vici.Session(s)
        
        v.load_shared(shared_secret)
        print(f"[VICI] Chave ETSI {key_id[:8]}... injetada.", flush=True)

        # Tenta iniciar a conexão
        for msg in v.initiate({"child": CONN_NAME}):
             pass # Consome o generator para executar o comando
            
    except Exception as e:
        print(f"[VICI] Erro: {e}", flush=True)
    finally:
        if s:
            s.close()

if __name__ == "__main__":
    print(f"Iniciando Adapter ETSI para {MY_HOSTNAME} -> Peer: {PEER_HOSTNAME}...", flush=True)
    time.sleep(5)
    
    last_key_id = None

    while True:
        key_data = fetch_key_etsi()
        
        if key_data:
            kid = key_data["key_id"]
            khex = key_data["key_hex"]
            
            if kid != last_key_id:
                print(f"[Adapter] Nova chave recebida do Quditto: {kid}", flush=True)
                inject_and_initiate(khex, kid)
                last_key_id = kid
        
        time.sleep(5)