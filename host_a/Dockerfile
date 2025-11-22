# Use Ubuntu 22.04 como base
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Instalar dependências do sistema (StrongSwan, GStreamer, utils de rede)
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

RUN pip3 install requests psutil vici

WORKDIR /app

COPY kms_adapter_vici.py /app/

CMD /usr/lib/ipsec/charon & \
    sleep 5 && \
    python3 kms_adapter_vici.py