from openai import OpenAI
from typing import List, Dict, Optional, Any
import logging
import json

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
    
    
    @staticmethod
    def generate_area_description(
        api_key: str,
        area_data: Dict[str, Any],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> str:
        """
        Gera uma descrição inteligente de uma área baseada em seus dados.
        
        Args:
            api_key: Chave de API da OpenAI
            area_data: Dicionário contendo todos os dados da área (coordenadas, plantas, observações)
            model: Modelo a ser utilizado (default: gpt-3.5-turbo)
            temperature: Controla a criatividade (0-2)
            max_tokens: Número máximo de tokens na resposta
            
        Returns:
            String com a descrição gerada
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            # Inicializa o cliente da OpenAI
            client = OpenAI(api_key=api_key)
            
            # Prepara o contexto para a IA
            system_prompt = """Você é um especialista em ecologia e análise de dados botânicos. 
Sua tarefa é analisar dados de uma área de monitoramento de plantas e gerar uma descrição concisa e informativa.

Os dados incluem:
- Coordenadas geográficas da área (polígono)
- Plantas encontradas na área (espécies)
- Localizações específicas de cada planta (latitude, longitude, elevação)
- Observações fenológicas ao longo do tempo (datas, fenofases, status de floração)

Gere uma descrição que:
1. Resuma a localização geográfica da área
2. Liste as espécies de plantas presentes
3. Descreva padrões de floração observados
4. Mencione o período de tempo coberto pelas observações
5. Seja concisa (máximo 3-4 frases)

A descrição deve ser em português e focada em informações úteis para pesquisadores e gestores ambientais."""

            # Prepara os dados da área em formato legível
            user_message = f"""Analise os seguintes dados e gere uma descrição:

Área ID: {area_data.get('id')}

Coordenadas do Polígono:
{json.dumps(area_data.get('coordinates', []), indent=2)}

Plantas e Observações:
{json.dumps(area_data.get('plants', []), indent=2, default=str)}

Gere uma descrição concisa e informativa desta área."""

            logger.info(f"Gerando descrição para área {area_data.get('id')}")
            
            # Faz a requisição para a API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            description = response.choices[0].message.content.strip()
            
            logger.info(f"Descrição gerada com sucesso - Tokens usados: {response.usage.total_tokens}")
            
            return description
            
        except Exception as e:
            logger.error(f"Erro ao gerar descrição da área: {str(e)}")
            raise Exception(f"Erro ao gerar descrição: {str(e)}")
