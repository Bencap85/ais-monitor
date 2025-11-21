FROM python:3.11-slim

WORKDIR /app

ENV KAFKA_ADDRESS host.docker.internal:9092

COPY src .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ping utility
RUN apt update && apt install -y iputils-ping

CMD ["python", "-u", "main.py"]
