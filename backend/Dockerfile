FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/logs && chmod -R 777 /app/logs  
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]