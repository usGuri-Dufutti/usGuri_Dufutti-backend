from fastapi import APIRouter, HTTPException, status
from typing import Dict
import logging

from schemas.openai_chat import ChatRequest, ChatResponse, ErrorResponse
from services.openai_service import OpenAIService
from core.config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat com OpenAI GPT-3.5 Turbo",
    description="Envia uma mensagem para o modelo GPT-3.5 Turbo e retorna a resposta",
    responses={
        200: {
            "description": "Resposta bem-sucedida do chat",
            "model": ChatResponse
        },
        400: {
            "description": "Requisição inválida (API key inválida, parâmetros incorretos, etc.)",
            "model": ErrorResponse
        },
        500: {
            "description": "Erro interno do servidor ou erro na API da OpenAI",
            "model": ErrorResponse
        }
    }
)
async def chat_with_openai(request: ChatRequest) -> ChatResponse:
    """
    Endpoint para chat com OpenAI GPT-3.5 Turbo.
    
    Este endpoint permite enviar mensagens para o modelo GPT-3.5 Turbo da OpenAI
    e receber respostas em tempo real. A API key deve ser fornecida no corpo da requisição.
    
    Args:
        request: Objeto ChatRequest contendo:
            - message: A mensagem a ser enviada
            - api_key: Chave de API da OpenAI
            - model: Modelo a ser usado (padrão: gpt-3.5-turbo)
            - temperature: Nível de criatividade (0-2, padrão: 0.7)
            - max_tokens: Número máximo de tokens na resposta (padrão: 500)
            - conversation_history: Histórico opcional de conversas anteriores
    
    Returns:
        ChatResponse: Objeto contendo:
            - response: A resposta gerada pela IA
            - model: Modelo utilizado
            - tokens_used: Quantidade de tokens consumidos
            - finish_reason: Motivo de finalização da geração
    
    Raises:
        HTTPException: 400 se a API key for inválida
        HTTPException: 500 se houver erro na comunicação com OpenAI
    """
    try:
        # Define a API key: usa a do request ou a do .env
        api_key = request.api_key or settings.OPENAI_API_KEY
        
        # Validação da API key
        if not api_key:
            logger.warning("API key não fornecida")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key não fornecida. Forneça na requisição ou configure no .env (OPENAI_API_KEY)."
            )
        
        if not OpenAIService.validate_api_key(api_key):
            logger.warning("Tentativa de uso com API key inválida")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key inválida. A chave deve começar com 'sk-' e ter formato válido."
            )
        
        # Validação da mensagem
        if not request.message or not request.message.strip():
            logger.warning("Tentativa de envio de mensagem vazia")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A mensagem não pode estar vazia."
            )
        
        # Converte conversation_history de Pydantic para dict se existir
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        logger.info(f"Processando requisição de chat - Modelo: {request.model}")
        
        # Chama o service para processar a requisição
        result = OpenAIService.create_chat_completion(
            api_key=api_key,
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            conversation_history=conversation_history
        )
        
        # Retorna a resposta
        return ChatResponse(**result)
        
    except HTTPException:
        # Re-lança HTTPExceptions (erros de validação)
        raise
        
    except Exception as e:
        # Captura erros da OpenAI API ou outros erros não esperados
        logger.error(f"Erro ao processar chat: {str(e)}")
        
        # Mensagem de erro amigável para o usuário
        error_message = str(e)
        if "api_key" in error_message.lower():
            detail = "API key rejeitada pela OpenAI. Verifique se a chave está correta e ativa."
        elif "rate_limit" in error_message.lower():
            detail = "Limite de requisições excedido. Tente novamente em alguns instantes."
        elif "insufficient_quota" in error_message.lower():
            detail = "Quota da API key excedida. Verifique seu saldo na OpenAI."
        else:
            detail = f"Erro ao processar requisição com a OpenAI: {error_message}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get(
    "/health",
    summary="Verifica status do serviço",
    description="Endpoint para verificar se o serviço de chat está funcionando"
)
async def health_check() -> Dict[str, str]:
    """
    Verifica o status do serviço de chat.
    
    Returns:
        Dict indicando que o serviço está operacional
    """
    return {
        "status": "healthy",
        "service": "OpenAI Chat Service",
        "version": "1.0.0"
    }
