from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from app.config import settings
from app.services.whisper_service import whisper_service
from app.services.video_service import video_service
from app.services.gpt_service import gpt_service

router = APIRouter(prefix="/video", tags=["video"])

def cleanup_files(*file_paths):
    """Remove múltiplos arquivos após processamento"""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Erro ao remover arquivo {file_path}: {e}")

@router.post("/description")
async def generate_video_description(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Análise COMPLETA de vídeo: áudio (transcrição) + visual (frames)
    
    Processo:
    1. Recebe vídeo
    2. Extrai áudio → transcreve com Whisper
    3. Extrai frames → análise visual
    4. GPT-4 Vision analisa TUDO junto
    5. Retorna descrição completa
    """
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
        )
    
    unique_id = str(uuid.uuid4())
    video_filename = f"{unique_id}{file_ext}"
    video_path = os.path.join(settings.UPLOAD_DIR, video_filename)
    audio_path = None
    
    try:
        # Salvar vídeo
        print(f"📹 Recebendo vídeo: {file.filename}")
        content = await file.read()
        
        if len(content) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        with open(video_path, "wb") as f:
            f.write(content)
        print(f"✅ Vídeo salvo: {video_path}")
        
        # Extrair áudio E frames
        print("🎵 Extraindo áudio e frames...")
        audio_path, frames_base64 = video_service.extract_audio_and_frames(video_path, num_frames=6)
        print(f"✅ Áudio extraído: {audio_path}")
        print(f"✅ Frames extraídos: {len(frames_base64)}")
        
        # Transcrever áudio com Whisper
        print("🎤 Transcrevendo áudio com Whisper...")
        transcription_result = whisper_service.transcribe(audio_path)
        transcription_text = transcription_result["text"]
        print(f"✅ Transcrição completa: {len(transcription_text)} caracteres")
        
        # Analisar TUDO com GPT-4 Vision (áudio + visual)
        print("🤖 Analisando com GPT-4 Vision...")
        description = gpt_service.analyze_video_complete(frames_base64, transcription_text)
        print("✅ Análise completa!")
        
        # Salvar resultado
        desc_filename = f"{unique_id}_description.txt"
        desc_path = os.path.join(settings.OUTPUT_DIR, desc_filename)
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(f"DESCRIÇÃO COMPLETA DO VÍDEO\n")
            f.write(f"(Análise: Visual + Áudio)\n\n")
            f.write(f"{description}\n\n")
            f.write(f"--- TRANSCRIÇÃO COMPLETA ---\n")
            f.write(transcription_text)
        
        # Limpar arquivos temporários
        background_tasks.add_task(cleanup_files, video_path, audio_path)
        
        return JSONResponse(content={
            "success": True,
            "description": description,
            "transcription": transcription_text,
            "language": transcription_result["language"],
            "frames_analyzed": len(frames_base64),
            "file": f"/outputs/{desc_filename}"
        })
    
    except Exception as e:
        cleanup_files(video_path, audio_path)
        raise HTTPException(status_code=500, detail=f"Erro ao processar vídeo: {str(e)}")
