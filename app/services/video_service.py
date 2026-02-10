import ffmpeg
import os
import base64
from typing import List, Tuple
from app.config import settings

class VideoService:
    def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """
        Extrai o áudio de um arquivo de vídeo
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            output_path: Caminho para salvar o áudio
            
        Returns:
            Caminho do arquivo de áudio extraído
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")
        
        if output_path is None:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.UPLOAD_DIR, f"{video_name}_audio.mp3")
        
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='libmp3lame', ab='192k')
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True, quiet=True)
            return output_path
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"Erro ao extrair áudio: {error_message}")
    
    def extract_frames(self, video_path: str, num_frames: int = 6) -> List[str]:
        """
        Extrai frames do vídeo em intervalos regulares e retorna como base64
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            num_frames: Número de frames para extrair
            
        Returns:
            Lista de frames em formato base64
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")
        
        try:
            # Obter duração do vídeo
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            
            # Calcular intervalos para extrair frames
            interval = duration / (num_frames + 1)
            frames_base64 = []
            
            # Criar diretório temporário para frames
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            frames_dir = os.path.join(settings.UPLOAD_DIR, f"{video_name}_frames")
            os.makedirs(frames_dir, exist_ok=True)
            
            # Extrair frames
            for i in range(num_frames):
                timestamp = interval * (i + 1)
                frame_path = os.path.join(frames_dir, f"frame_{i}.jpg")
                
                # Extrair frame no timestamp especificado
                (
                    ffmpeg
                    .input(video_path, ss=timestamp)
                    .filter('scale', 512, -1)  # Redimensionar para economizar tokens
                    .output(frame_path, vframes=1, format='image2', vcodec='mjpeg')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
                
                # Converter para base64
                with open(frame_path, 'rb') as f:
                    frame_base64 = base64.b64encode(f.read()).decode('utf-8')
                    frames_base64.append(frame_base64)
                
                # Limpar arquivo temporário
                os.remove(frame_path)
            
            # Remover diretório temporário
            os.rmdir(frames_dir)
            
            return frames_base64
        
        except Exception as e:
            raise Exception(f"Erro ao extrair frames do vídeo: {str(e)}")

# Instance
video_service = VideoService()
