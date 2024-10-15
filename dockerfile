FROM python:3.12-alpine

RUN apk add --no-cache gcc musl-dev

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

ENV DB_PATH="sqlite:///app/database/game_tg_bot.db"

CMD ["python", "main.py"]

