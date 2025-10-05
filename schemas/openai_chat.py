from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Modelo de mensagem individual no chat"""
    role: str = Field(..., description="Papel da mensagem: 'system', 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatRequest(BaseModel):
    """Requisição para o chat com OpenAI"""
    message: str = Field(..., description="Mensagem do usuário", example="Olá, como você está?")
    api_key: Optional[str] = Field(None, description="Chave de API da OpenAI (opcional se configurada no .env)")
    model: str = Field(default="gpt-3.5-turbo", description="Modelo do OpenAI a ser usado")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperatura para criatividade das respostas")
    max_tokens: Optional[int] = Field(default=500, description="Número máximo de tokens na resposta")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, 
        description="Histórico de conversa opcional para manter contexto"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Qual é a capital do Brasil?",
                "api_key": "sk-...",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }


class ChatResponse(BaseModel):
    """Resposta do chat com OpenAI"""
    response: str = Field(..., description="Resposta gerada pela IA")
    model: str = Field(..., description="Modelo utilizado")
    tokens_used: int = Field(..., description="Número de tokens utilizados na requisição")
    finish_reason: str = Field(..., description="Razão pela qual a geração foi finalizada")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "A capital do Brasil é Brasília.",
                "model": "gpt-3.5-turbo",
                "tokens_used": 50,
                "finish_reason": "stop"
            }
        }


class ErrorResponse(BaseModel):
    """Resposta de erro"""
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais do erro")
