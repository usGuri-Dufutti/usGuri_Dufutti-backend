# usGuri_Dufutti-backend
Como rodar->
docker compose up --build

inserir dados no banco->
docker compose exec backend python -m utils.convertData

Testar se foram inseridos->
docker compose exec postgres psql -U paster -d flowerDB


http://localhost:8000/ -> rota padrão

# Importante

Usar branch para desenvolver task Ex: feat/<task_name>
