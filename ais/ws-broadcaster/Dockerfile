FROM python:3.11-slim

WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY src .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]