from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import audio, video

# Criar aplicação FastAPI
app = FastAPI(
    title="Pesquise+Hub API",
    description="API para transcrição de áudio e geração de descrições de vídeo",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# Incluir routers
app.include_router(audio.router)
app.include_router(video.router)

@app.get("/")
async def root():
    return {
        "message": "Pesquise+Hub API",
        "endpoints": {
            "audio_transcription": "/audio/transcribe",
            "video_description": "/video/description",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)