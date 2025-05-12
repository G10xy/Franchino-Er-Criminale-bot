FROM python:3.9-slim-buster

WORKDIR /app

COPY src/ .
COPY requirements.txt .
COPY registry-fec-bot.xlsx .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python3", "bot.py"]
