# PoC: Integração de VPN IPsec com Distribuição Quântica de Chaves (QKD)

Este repositório contém uma **Prova de Conceito (PoC)** que demonstra a integração de tecnologias de criptografia clássica (IPsec/IKEv2) com simulação de **Distribuição Quântica de Chaves (QKD)**.

O projeto implementa uma arquitetura **SDN-QKD** (Software-Defined Networking with QKD) em contêineres Docker, onde as chaves de criptografia do túnel VPN são rotacionadas dinamicamente via software e sincronizadas através de uma API compatível com o padrão **ETSI GS QKD 014**.

## Objetivo

Demonstrar a viabilidade técnica de substituir chaves pré-compartilhadas estáticas (PSK) em túneis VPN por chaves de alta entropia geradas e distribuídas dinamicamente, aumentando a segurança contra ataques futuros (incluindo *Harvest Now, Decrypt Later*).

## Estrutura do Repositório

* `/host_a`: Configurações e scripts do Host A (Alice).
* `/host_b`: Configurações e scripts do Host B (Bob).
* `/quditto`: Mock do provedor QKD (API ETSI).
* `docker-compose.yml`: Orquestração do ambiente.

## Arquitetura do Sistema (Abordagem SDN)

O sistema segue o paradigma **SDN (Redes Definidas por Software)**, separando claramente o plano de controle do plano de dados:

1.  **Plano de Controle (Software/Python):**
    * **Quditto (Mock QKD):** Servidor central que simula a geração de chaves quânticas e expõe a API REST **ETSI GS QKD 014**.
    * **KMS Adapter:** Agentes inteligentes em cada nó (Alice e Bob) que negociam chaves com o Quditto e reprogramam a criptografia em tempo real.

2.  **Plano de Dados (Kernel/IPsec):**
    * **StrongSwan (Charon):** Responsável apenas pelo encaminhamento e encapsulamento de pacotes (ESP).
    * O daemon é controlado programaticamente via protocolo **VICI**, permitindo a injeção de chaves na memória sem reinicialização do serviço.

## Nota Técnica: Arquitetura de Rede e Traffic Selectors

Uma parte crítica desta implementação é a configuração de **IPs Virtuais** (`10.10.1.1` e `10.10.2.1`). Isso é necessário devido ao funcionamento dos **Traffic Selectors** do IPsec.

* **O Problema:** Por padrão, o Docker atribui IPs da faixa `172.18.x.x`. No entanto, políticas de segurança do IPsec (`ipsec.conf`) estão configuradas para proteger estritamente o tráfego entre as sub-redes `10.10.1.0/24` e `10.10.2.0/24` (Que pode ser facilmente trocado). Se o tráfego se originar dos IPs nativos do Docker, ele não corresponde à política (*Traffic Selector mismatch*) e é ignorado pelo StrongSwan.
* **A Solução:** Adicionamos manualmente IPs secundários ("Alias") às interfaces de rede dos contêineres. Ao forçar o tráfego a sair por esses IPs, garantimos que os pacotes correspondam à regra `leftsubnet`/`rightsubnet`, acionando a criptografia ESP.

## Como Executar

### Pré-requisitos
* Docker
* Docker Compose

### Inicialização

1.  Construa e inicie os contêineres:
    ```bash
    docker-compose up --build
    ```

2.  **Configuração de Rede (Passo Obrigatório):**
    Como explicado na nota técnica, é necessário configurar as interfaces virtuais manualmente para ativar o tunelamento. Execute em terminais separados:

    *No Host A (Alice):*
    ```bash
    docker exec -it host-a ip addr add 10.10.1.1/24 dev eth0
    ```

    *No Host B (Bob):*
    ```bash
    docker exec -it host-b ip addr add 10.10.2.1/24 dev eth0
    ```

## 🧪 Validação e Testes

Para validar o funcionamento, utilize os seguintes comandos em terminais separados:

### 1. Verificar Status do Túnel
Confira se a conexão IPsec (IKE_SA e CHILD_SA) foi estabelecida com a chave QKD injetada:
```bash
docker exec -it host-a ipsec statusall
```
Saída esperada: *Security Associations (1 up, 0 connecting)*

### 2. Teste de Conectividade (Ping)
este o túnel forçando a origem do pacote para o IP Virtual:
``` bash
docker exec -it host-a ping -c 4 -I 10.10.1.1 10.10.2.1
```

### 3. Verificar Criptografia (Sniffing)
Para provar que os dados não estão em texto plano, capture os pacotes na interface física:
``` bash
docker exec -it host-a tshark -i eth0 -f "esp"
```

### 4. Transmissão de Vídeo em Tempo Real (GStreamer)
Streaming de vídeo H.264 sobre a VPN com baixa latência:
*No Host B (Receptor):*
``` bash
docker exec -it host-b gst-launch-1.0 -v udpsrc port=5000 ! \
 "application/x-rtp, media=video, clock-rate=90000, encoding-name=H264, payload=96" ! \
 rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
```

*No Host A (Emissor):*
``` bash
docker exec -it host-a gst-launch-1.0 -v videotestsrc is-live=true ! \
 video/x-raw,width=640,height=480 ! x264enc tune=zerolatency ! \
 rtph264pay config-interval=1 pt=96 ! udpsink host=10.10.2.1 port=5000
```
