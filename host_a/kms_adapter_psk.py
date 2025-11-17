# kms_adapter_psk.py
import requests, subprocess, time, os, json

QUDITTO = "http://quditto:8000/keys/next"
IPSEC_SECRETS = "/etc/ipsec.secrets"
CONN_NAME = "qkd-poc"

def fetch_key():
    r = requests.get(QUDITTO, timeout=5)
    r.raise_for_status()
    return r.json()

def install_psk(hexkey):
    psk = hexkey
    content = f"@hostA @hostB : PSK \"{psk}\"\n"
    with open(IPSEC_SECRETS, "w") as f:
        f.write(content)
    os.chmod(IPSEC_SECRETS, 0o600)
    print("Reloading strongSwan IPsec configuration...")
    subprocess.run(["ipsec", "reload"], check=True)
    #subprocess.run(["ipsec", "up", CONN_NAME], check=True)

if __name__ == "__main__":
    while True:
        try:
            data = fetch_key()
            print("Got key_id:", data["key_id"])
            install_psk(data["enc_key_hex"])
        except Exception as e:
            print("Adapter error:", e)
        time.sleep(60)  # roda a cada minuto (ajuste conforme necessário)
