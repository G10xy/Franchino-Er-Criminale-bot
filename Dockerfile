FROM python:3.10-slim

WORKDIR /app

COPY src/ .
COPY requirements.txt .
COPY data/ .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python3", "bot.py"]
