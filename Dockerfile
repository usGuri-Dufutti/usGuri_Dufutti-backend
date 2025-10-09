FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Instalar somente libpq-dev (psycopg2-binary dispensa compilação)
RUN apt-get update && apt-get install -y libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render vai injetar a porta em $PORT
ENV PORT=8000
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
