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
            system_prompt = """You are an expert in ecology and botanical data analysis.
Your task is to analyze phenological data from a plant monitoring area and generate a comprehensive and informative description.

The data includes:
- Plant species found in the area
- Elevation data (height in meters)
- Phenological observations over time (dates, phenophases, blooming status, descriptions)

IMPORTANT INSTRUCTIONS:
- DO NOT mention latitude or longitude coordinates
- DO NOT mention any area IDs, identification numbers, or area codes
- DO NOT say the location or area UNDER ANALYSIS. avoid saying under analysis or area under analysis.
- DO NOT use phrases like "the area under analysis", "area ID", "in area X", or "area number Y"
- Start your description naturally, for example: "In the location...", "The observed species...", "In this location...", or "The area..."
- Only mention elevation/height when relevant
- Focus on phenological phases (leaf budding, flowering, fruiting, etc.)
- Analyze flowering patterns and their implications
- Provide insights about the suitability of the location for planting
- Follow the structure and writing style of the examples below

EXAMPLE 1:
"In the analyzed location, most species predominantly showed the beginning of leaf budding, with flowering records restricted to macrophyllum in April. This suggests that flowering is limited or occurs in a concentrated manner in few species, while the majority remains in vegetative phase for much of the year. Despite reduced flowering, consistent leaf growth indicates that the environment offers adequate conditions for plant development, making the location favorable for planting, although it is not characterized by abundant flowering periods."

EXAMPLE 2:
"The observed species predominantly showed the beginning of leaf budding and ripe fruits, with no flowering records throughout 2024. This indicates that, during the monitored period, the location did not favor expressive flowering periods, but vegetative growth and fruiting proved to be consistent. Thus, the environment is suitable for plant development, although it is not characterized by abundant flowering, being more suitable for those seeking cultivation with leaf growth and fruit production."

The description must be in English and focused on phenological analysis useful for researchers and environmental managers."""

            # Prepara os dados da área em formato legível
            user_message = f"""Analyze the following phenological data and generate a description following the examples provided:

Plants and Phenological Observations:
{json.dumps(area_data.get('plants', []), indent=2, default=str)}

Generate a comprehensive 1-2 paragraph description following the style and structure of the examples. Focus on phenological patterns, flowering behavior, and suitability for cultivation. Start your description naturally without mentioning any area identification numbers."""

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
    
    
    @staticmethod
    def answer_area_question(
        api_key: str,
        area_data: Dict[str, Any],
        question: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Responde a uma pergunta específica sobre uma área baseada em seus dados.
        
        Args:
            api_key: Chave de API da OpenAI
            area_data: Dicionário contendo todos os dados da área (coordenadas, plantas, observações)
            question: Pergunta do usuário sobre a área
            model: Modelo a ser utilizado (default: gpt-3.5-turbo)
            temperature: Controla a criatividade (0-2)
            max_tokens: Número máximo de tokens na resposta
            
        Returns:
            Dict contendo a resposta e metadados
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            # Inicializa o cliente da OpenAI
            client = OpenAI(api_key=api_key)
            
            # Prepara o contexto para a IA
            system_prompt = """You are an expert in ecology, botany, and phenological data analysis.
Your task is to answer questions about a specific plant monitoring area based on its data.

The data includes:
- Plant species found in the area
- Geographic coordinates of the area (polygon)
- Elevation data (height in meters)
- Phenological observations over time (dates, phenophases, blooming status, descriptions)

IMPORTANT INSTRUCTIONS:
- Answer based ONLY on the provided data
- Be specific and accurate in your responses
- Focus on phenological information (leaf budding, flowering, fruiting, etc.)
- Mention specific species when relevant
- If the data doesn't contain information to answer the question, say so clearly
- Provide insights about patterns, trends, or ecological significance when appropriate
- Keep your answers clear, informative, and professional
- ALWAYS answer in the SAME LANGUAGE as the user's question
- Write in a natural, conversational style as a single continuous flowing text
- DO NOT use ANY formatting characters: no **, no -, no #, no bullets, no quotation marks "", no apostrophes '', no backticks ``
- When mentioning species names, write them directly without any quotes or special characters (e.g., write "the brevifolia species" not "the \"brevifolia\" species")
- DO NOT use line breaks or paragraph separators (no \n)
- Write everything as one continuous paragraph
- Make your answers flow naturally like a conversation
- Example: Instead of "brevifolia" and "ramosissima" write: brevifolia and ramosissima

Your answers should be helpful for researchers, environmental managers, and anyone interested in understanding the phenological patterns of the area."""

            # Prepara os dados da área em formato legível
            user_message = f"""Based on the following phenological data from a monitoring area, please answer the user's question:

Area Data:
- Coordinates: {len(area_data.get('coordinates', []))} points defining the area polygon
- Number of plants monitored: {len(area_data.get('plants', []))}

Plants and Phenological Observations:
{json.dumps(area_data.get('plants', []), indent=2, default=str)}

User Question: {question}

Please provide a clear and informative answer based on the available data."""

            logger.info(f"Respondendo pergunta sobre área {area_data.get('id')}: {question[:50]}...")
            
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
            
            answer = response.choices[0].message.content.strip()
            
            # Remove quebras de linha e múltiplos espaços
            answer = answer.replace('\n', ' ').replace('\r', ' ')
            # Remove aspas duplas e simples
            answer = answer.replace('"', '').replace("'", '')
            # Remove múltiplos espaços seguidos
            while '  ' in answer:
                answer = answer.replace('  ', ' ')
            answer = answer.strip()
            
            result = {
                "answer": answer,
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Resposta gerada com sucesso - Tokens usados: {result['tokens_used']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao responder pergunta sobre área: {str(e)}")
            raise Exception(f"Erro ao processar pergunta: {str(e)}")