FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code + artifacts
COPY backend/ /app/
COPY model_artifacts/ /app/model_artifacts/
COPY knowledge/ /app/knowledge/
COPY sample_data/ /app/sample_data/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
