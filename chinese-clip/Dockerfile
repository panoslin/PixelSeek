FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies and CN-CLIP from GitHub
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Set environment variables for model caching
ENV TORCH_HOME=/root/.cache/clip

CMD ["python", "app.py"]