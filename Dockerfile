FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# NÃO atualiza o pip (pip 26 quebra o openai-whisper)
# Instala setuptools explicitamente para garantir pkg_resources
RUN pip install --no-cache-dir setuptools==69.0.0 wheel

# Instala torch CPU-only
RUN pip install --no-cache-dir \
    torch==2.1.2 \
    --index-url https://download.pytorch.org/whl/cpu

# Instala whisper sem ambiente de build isolado (usa setuptools já instalado)
RUN pip install --no-cache-dir --no-build-isolation openai-whisper==20231117

# Instala restante
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
RUN mkdir -p uploads outputs

ENV OPENAI_API_KEY=""
ENV WHISPER_MODEL="base"
ENV MAX_FILE_SIZE_MB="100"
ENV ALLOW_ORIGINS="*"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]