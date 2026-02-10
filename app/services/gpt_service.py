from openai import OpenAI
from app.config import settings

class GPTService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_description(self, transcription_text: str, max_tokens: int = 500) -> str:
        """
        Gera uma descrição concisa a partir de um vídeo.
        
        Args:
            transcription_text: Texto da transcrição
            max_tokens: Número máximo de tokens na resposta
            
        Returns:
            Descrição gerada pelo GPT
        """
        # Limitar o tamanho da transcrição para reduzir custos
        max_input_chars = 3000
        if len(transcription_text) > max_input_chars:
            transcription_text = transcription_text[:max_input_chars] + "..."
        
        prompt = f"""Você é um assistente que cria descrições concisas e informativas de vídeos baseadas em transcrições.

Tarefa: Analise a transcrição abaixo e crie uma descrição clara e objetiva do conteúdo do vídeo.

A descrição deve:
- Ter entre 2-4 parágrafos
- Destacar os principais tópicos abordados
- Ser útil para alguém que deseja saber do que se trata o vídeo
- Usar linguagem clara e profissional

Transcrição:
{transcription_text}

Descrição:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em criar descrições de vídeos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Erro ao gerar descrição com GPT: {str(e)}")
    
    def analyze_video_complete(self, frames_base64: list, transcription_text: str, max_tokens: int = 700) -> str:
        """
        Análise COMPLETA: visual (frames) + áudio (transcrição)
        
        Args:
            frames_base64: Frames do vídeo
            transcription_text: Texto transcrito do áudio
            max_tokens: Tokens máximos
            
        Returns:
            Descrição completa do vídeo
        """
        try:
            # Limitar transcrição para controlar custos
            max_chars = 2000
            if len(transcription_text) > max_chars:
                transcription_text = transcription_text[:max_chars] + "..."
            
            # Preparar conteúdo
            content = [
                {
                    "type": "text",
                    "text": f"""Analise este vídeo COMPLETAMENTE usando:

1. CONTEÚDO VISUAL (frames abaixo)
2. CONTEÚDO DE ÁUDIO (transcrição):

--- TRANSCRIÇÃO ---
{transcription_text}
--- FIM TRANSCRIÇÃO ---

Crie uma descrição detalhada que:
- Descreva o que ACONTECE visualmente (ações, pessoas, objetos, cenário)
- Resuma o que está sendo DITO/FALADO
- Integre áudio e vídeo numa descrição coerente
- Tenha 3-5 parágrafos
- Seja útil para entender TODO o conteúdo

Descrição:"""
                }
            ]
            
            # Adicionar frames
            for frame in frames_base64[:6]:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame}",
                        "detail": "low"
                    }
                })
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Erro ao analisar vídeo: {str(e)}")

# Instance
gpt_service = GPTService()
