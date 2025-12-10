FROM ml-base:latest

WORKDIR /app

# Install this system level dependency used by openvc
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# Copy only requirements first to leverage Docker caching
# COPY requirements.txt .

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install -r requirements.txt

# Now copy the rest of your code
COPY . .

CMD ["python", "server.py"]
