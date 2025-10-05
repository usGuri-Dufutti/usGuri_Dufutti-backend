from openai import OpenAI
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service para interagir com a API da OpenAI.
    Segue as melhores práticas de separação de responsabilidades.
    """
    
    @staticmethod
    def create_chat_completion(
        api_key: str,
        message: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Cria uma completação de chat usando a API da OpenAI.
        
        Args:
            api_key: Chave de API da OpenAI
            message: Mensagem do usuário
            model: Modelo a ser utilizado (default: gpt-3.5-turbo)
            temperature: Controla a criatividade (0-2)
            max_tokens: Número máximo de tokens na resposta
            conversation_history: Histórico de mensagens anteriores
            
        Returns:
            Dict com a resposta da API
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            # Inicializa o cliente da OpenAI com a API key
            client = OpenAI(api_key=api_key)
            
            # Monta o array de mensagens
            messages = []
            
            # Adiciona histórico de conversas se existir
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
            
            # Adiciona a mensagem atual do usuário
            messages.append({
                "role": "user",
                "content": message
            })
            
            logger.info(f"Enviando requisição para OpenAI - Modelo: {model}")
            
            # Faz a requisição para a API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extrai informações da resposta
            result = {
                "response": response.choices[0].message.content,
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Resposta recebida - Tokens usados: {result['tokens_used']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao comunicar com OpenAI: {str(e)}")
            raise Exception(f"Erro ao processar requisição: {str(e)}")
    
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Valida se a API key possui o formato esperado.
        
        Args:
            api_key: Chave de API a ser validada
            
        Returns:
            True se a chave é válida, False caso contrário
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # API keys da OpenAI começam com 'sk-'
        if not api_key.startswith("sk-"):
            return False
        
        # Deve ter comprimento mínimo
        if len(api_key) < 20:
            return False
        
        return True
