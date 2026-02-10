from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from app.config import settings
from app.services.whisper_service import whisper_service

router = APIRouter(prefix="/audio", tags=["audio"])

def cleanup_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Erro ao remover arquivo {file_path}: {e}")

@router.post("/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
        )
    
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}{file_ext}"
    audio_path = os.path.join(settings.UPLOAD_DIR, audio_filename)
    
    try:
        content = await file.read()
        
        if len(content) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Tamanho máximo: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        with open(audio_path, "wb") as f:
            f.write(content)
        
        result = whisper_service.transcribe(audio_path)
        
        txt_filename = f"{unique_id}.txt"
        txt_path = os.path.join(settings.OUTPUT_DIR, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        srt_filename = f"{unique_id}.srt"
        srt_path = os.path.join(settings.OUTPUT_DIR, srt_filename)
        srt_content = whisper_service.generate_srt(result["segments"])
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        background_tasks.add_task(cleanup_file, audio_path)
        
        return JSONResponse(content={
            "success": True,
            "text": result["text"],
            "language": result["language"],
            "files": {
                "txt": f"/outputs/{txt_filename}",
                "srt": f"/outputs/{srt_filename}"
            },
            "segments_count": len(result["segments"])
        })
    
    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")
