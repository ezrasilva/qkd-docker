# Use Ubuntu 22.04 como base, conforme o plano
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar todas as dependências do Passo 0
RUN apt-get update && apt-get install -y \
    strongswan \
    strongswan-swanctl \
    libstrongswan-extra-plugins \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-libav \
    tshark \
    iperf3 \
    python3 \
    python3-pip \
    git \
    iproute2 \
    curl \
    nano \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python do adapter
RUN pip3 install requests psutil

# Copiar o adapter para dentro do contêiner
COPY kms_adapter_psk.py /app/
WORKDIR /app

# (Opcional) Copiar config do IPsec na build
# COPY ipsec.conf /etc/ipsec.conf

# Comando para manter o contêiner rodando
# O strongSwan será iniciado por script ou docker-compose
CMD ["tail", "-f", "/dev/null"]