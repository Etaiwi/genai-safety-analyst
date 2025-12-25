FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio \
 && pip install --no-cache-dir -r requirements.txt

# Copy only the app code (not tests, storage, etc.)
COPY src/ ./src/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
