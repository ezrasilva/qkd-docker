FROM python:3.11-slim

WORKDIR /app

# Instala as dependências do servidor web
RUN pip install fastapi uvicorn

# Copia o script do mock
COPY mock_quditto_etsi.py /app/

# Expõe a porta 8000
EXPOSE 8000

# Inicia o servidor uvicorn
CMD ["uvicorn", "mock_quditto_etsi:app", "--host", "0.0.0.0", "--port", "8000"]