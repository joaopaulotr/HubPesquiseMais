FROM python:3.11-slim-bullseye

# Instalar ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/

# Criar diretórios necessários
RUN mkdir -p uploads outputs

# Variáveis de ambiente (definir na plataforma de deploy)
ENV OPENAI_API_KEY=""
ENV WHISPER_MODEL="base"
ENV MAX_FILE_SIZE_MB="100"

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
