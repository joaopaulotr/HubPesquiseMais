import whisper
import os
import shutil
from typing import Dict, Any
from app.config import settings
import imageio_ffmpeg

# Configurar FFmpeg para Whisper
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
ffmpeg_standard = os.path.join(ffmpeg_dir, "ffmpeg.exe")

# Criar cópia com nome padrão se não existir
if not os.path.exists(ffmpeg_standard):
    shutil.copy2(ffmpeg_exe, ffmpeg_standard)

# Adicionar ao PATH
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
os.environ["FFMPEG_BINARY"] = ffmpeg_standard

class WhisperService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            print(f"Carregando modelo Whisper '{settings.WHISPER_MODEL}'...")
            self._model = whisper.load_model(settings.WHISPER_MODEL)
            print("Modelo Whisper carregado com sucesso!")
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcreve um arquivo de áudio usando Whisper
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Dict contendo 'text' (texto completo) e 'segments' (segmentos com timestamps)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
        
        result = self._model.transcribe(audio_path, language="pt", verbose=False)
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }
    
    def generate_srt(self, segments: list) -> str:
        """
        Gera conteúdo SRT a partir dos segmentos do Whisper
        
        Args:
            segments: Lista de segmentos do Whisper
            
        Returns:
            String com conteúdo no formato SRT
        """
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = self._format_timestamp(segment['start'])
            end_time = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")
        
        return "\n".join(srt_content)
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Converte segundos para formato SRT (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# Singleton instance
whisper_service = WhisperService()
