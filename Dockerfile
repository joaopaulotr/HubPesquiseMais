FROM python:3.11-slim-bullseye

# Instalar ffmpeg e dependências de sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Atualizar pip e instalar torch CPU-only primeiro (evita baixar versão CUDA ~2GB)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
        torch==2.1.2 \
        --index-url https://download.pytorch.org/whl/cpu

# Instalar restante das dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ ./app/

# Criar diretórios necessários
RUN mkdir -p uploads outputs

# Variáveis de ambiente padrão (sobrescrever via .env ou docker-compose)
ENV OPENAI_API_KEY=""
ENV WHISPER_MODEL="base"
ENV MAX_FILE_SIZE_MB="100"
ENV ALLOW_ORIGINS="*"

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
