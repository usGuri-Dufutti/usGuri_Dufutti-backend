from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import logging

from db.session import SessionLocal
from models.area import Area, AreaCoordinate
from models.plant import Plant
from schemas.area import AreaCreate, AreaResponse, AreaListResponse, AreaChatRequest, AreaChatResponse
from services.openai_service import OpenAIService
from core.config import settings

from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
def create_area(area_data: AreaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova área com suas coordenadas (polígono)
    """
    # Criar a área
    new_area = Area()
    db.add(new_area)
    db.flush()  # Para obter o ID

    # Adicionar coordenadas
    for coord_data in area_data.coordinates:
        coordinate = AreaCoordinate(
            area_id=new_area.id,
            latitude=coord_data.latitude,
            longitude=coord_data.longitude,
            order=coord_data.order
        )
        db.add(coordinate)

    db.commit()
    db.refresh(new_area)

    # Carregar com relacionamentos
    area = db.query(Area).options(
        joinedload(Area.coordinates),
        joinedload(Area.plants)
            .joinedload(Plant.site),
        joinedload(Area.plants)
            .joinedload(Plant.observations)
    ).filter(Area.id == new_area.id).first()

    return area


@router.get("/", response_model=List[AreaListResponse])
@router.get("/areas/", response_model=List[AreaListResponse])
def list_areas(db: Session = Depends(get_db)):
    areas = db.query(Area).all()
    return [AreaListResponse.from_orm(area) for area in areas]



@router.get("/{area_id}", response_model=AreaResponse)
def get_area(area_id: int, db: Session = Depends(get_db)):
    """
    Retorna uma área específica com:
    - Coordenadas do polígono
    - Plantas da área
    - Site de cada planta (lat/long)
    - Até 1 observação por planta por mês (máx 12 meses)
    - Descrição gerada por IA (gera automaticamente se não existir)
    """
    area = db.query(Area).options(
        joinedload(Area.coordinates),
        joinedload(Area.plants)
            .joinedload(Plant.site),
        joinedload(Area.plants)
            .joinedload(Plant.observations)
    ).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área não encontrada")

    for plant in area.plants:
        # Agrupa observações por ano/mês
        month_dict = defaultdict(list)
        for obs in plant.observations:
            ym = (obs.observation_date.year, obs.observation_date.month)
            month_dict[ym].append(obs)

        # Seleciona a observação mais recente de cada mês
        monthly_obs = [max(obs_list, key=lambda o: o.observation_date)
                       for obs_list in month_dict.values()]

        # Ordena do mais recente ao mais antigo e limita a 12 meses
        plant.observations = sorted(monthly_obs, key=lambda o: o.observation_date, reverse=True)[:12]

    # Gera descrição automaticamente se não existir
    if not area.description:
        try:
            logger.info(f"Gerando descrição para área {area_id}")
            
            # Verifica se a API key está configurada
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY não configurada - descrição não será gerada")
            else:
                # Prepara os dados da área para enviar à IA
                area_data = {
                    "id": area.id,
                    "coordinates": [
                        {
                            "latitude": coord.latitude,
                            "longitude": coord.longitude,
                            "order": coord.order,
                            "id": coord.id
                        }
                        for coord in area.coordinates
                    ],
                    "plants": [
                        {
                            "species": plant.species,
                            "id": plant.id,
                            "site_id": plant.site_id,
                            "area_id": plant.area_id,
                            "site": {
                                "latitude": plant.site.latitude,
                                "longitude": plant.site.longitude,
                                "elevation": plant.site.elevation,
                                "id": plant.site.id
                            },
                            "observations": [
                                {
                                    "phenophase_id": obs.phenophase_id,
                                    "observation_date": obs.observation_date.isoformat(),
                                    "is_blooming": obs.is_blooming,
                                    "description": obs.description,
                                    "id": obs.id,
                                    "site_id": obs.site_id,
                                    "plant_id": obs.plant_id
                                }
                                for obs in plant.observations
                            ]
                        }
                        for plant in area.plants
                    ]
                }
                
                # Gera a descrição usando o serviço OpenAI
                description = OpenAIService.generate_area_description(
                    api_key=settings.OPENAI_API_KEY,
                    area_data=area_data
                )
                
                # Salva a descrição no banco de dados
                area.description = description
                db.commit()
                db.refresh(area)
                
                logger.info(f"Descrição gerada e salva com sucesso para área {area_id}")
                
        except Exception as e:
            logger.error(f"Erro ao gerar descrição para área {area_id}: {str(e)}")
            # Não falha a requisição se houver erro na geração da descrição
            # A área será retornada sem descrição

    return area

@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(area_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma área (as coordenadas são deletadas automaticamente por cascade)
    """
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(status_code=404, detail="Área não encontrada")

    # Remove area_id das plantas antes de deletar
    db.query(Plant).filter(Plant.area_id == area_id).update({"area_id": None})

    db.delete(area)
    db.commit()

    return None


@router.post("/{area_id}/chat", response_model=AreaChatResponse, status_code=status.HTTP_200_OK)
def chat_about_area(
    area_id: int, 
    chat_request: AreaChatRequest, 
    db: Session = Depends(get_db)
):
    """
    Permite fazer perguntas sobre uma área específica.
    A IA responderá baseada nos dados dessa área (plantas, observações, coordenadas).
    
    Args:
        area_id: ID da área sobre a qual fazer a pergunta
        chat_request: Objeto contendo a pergunta e configurações
        
    Returns:
        AreaChatResponse com a resposta da IA e metadados
        
    Raises:
        HTTPException: 404 se a área não for encontrada
        HTTPException: 400 se a API key for inválida ou pergunta vazia
        HTTPException: 500 se houver erro ao processar a pergunta
    """
    try:
        # Busca a área com todos os dados necessários
        area = db.query(Area).options(
            joinedload(Area.coordinates),
            joinedload(Area.plants)
                .joinedload(Plant.site),
            joinedload(Area.plants)
                .joinedload(Plant.observations)
        ).filter(Area.id == area_id).first()

        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área com ID {area_id} não encontrada"
            )

        # Validação da pergunta
        if not chat_request.question or not chat_request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A pergunta não pode estar vazia"
            )

        # Usa sempre a API key do .env
        api_key = settings.OPENAI_API_KEY
        
        # Validação da API key
        if not api_key:
            logger.warning("API key não configurada no .env")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Serviço não configurado. OPENAI_API_KEY não encontrada no servidor."
            )
        
        if not OpenAIService.validate_api_key(api_key):
            logger.warning("API key configurada no .env é inválida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Serviço mal configurado. API key inválida no servidor."
            )

        # Prepara os dados da área (similar ao get_area para descrição)
        # Agrupa observações por mês
        for plant in area.plants:
            month_dict = defaultdict(list)
            for obs in plant.observations:
                ym = (obs.observation_date.year, obs.observation_date.month)
                month_dict[ym].append(obs)

            # Seleciona a observação mais recente de cada mês
            monthly_obs = [max(obs_list, key=lambda o: o.observation_date)
                           for obs_list in month_dict.values()]

            # Ordena do mais recente ao mais antigo e limita a 12 meses
            plant.observations = sorted(monthly_obs, key=lambda o: o.observation_date, reverse=True)[:12]

        # Prepara os dados da área para enviar à IA
        area_data = {
            "id": area.id,
            "coordinates": [
                {
                    "latitude": coord.latitude,
                    "longitude": coord.longitude,
                    "order": coord.order,
                    "id": coord.id
                }
                for coord in area.coordinates
            ],
            "plants": [
                {
                    "species": plant.species,
                    "id": plant.id,
                    "site_id": plant.site_id,
                    "area_id": plant.area_id,
                    "site": {
                        "latitude": plant.site.latitude,
                        "longitude": plant.site.longitude,
                        "elevation": plant.site.elevation,
                        "id": plant.site.id
                    },
                    "observations": [
                        {
                            "phenophase_id": obs.phenophase_id,
                            "observation_date": obs.observation_date.isoformat(),
                            "is_blooming": obs.is_blooming,
                            "description": obs.description,
                            "id": obs.id,
                            "site_id": obs.site_id,
                            "plant_id": obs.plant_id
                        }
                        for obs in plant.observations
                    ]
                }
                for plant in area.plants
            ]
        }

        logger.info(f"Processando pergunta sobre área {area_id}: {chat_request.question[:50]}...")

        # Chama o serviço OpenAI para responder a pergunta
        # Usa configurações padrão fixas
        result = OpenAIService.answer_area_question(
            api_key=api_key,
            area_data=area_data,
            question=chat_request.question,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500
        )

        # Retorna a resposta
        return AreaChatResponse(
            question=chat_request.question,
            answer=result["answer"],
            area_id=area_id
        )

    except HTTPException:
        # Re-lança HTTPExceptions (erros de validação)
        raise
        
    except Exception as e:
        # Captura erros da OpenAI API ou outros erros não esperados
        logger.error(f"Erro ao processar chat sobre área {area_id}: {str(e)}")
        
        # Mensagem de erro amigável para o usuário
        error_message = str(e)
        if "api_key" in error_message.lower():
            detail = "API key rejeitada pela OpenAI. Verifique se a chave está correta e ativa."
        elif "rate_limit" in error_message.lower():
            detail = "Limite de requisições excedido. Tente novamente em alguns instantes."
        elif "insufficient_quota" in error_message.lower():
            detail = "Quota da API key excedida. Verifique seu saldo na OpenAI."
        else:
            detail = f"Erro ao processar pergunta: {error_message}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
