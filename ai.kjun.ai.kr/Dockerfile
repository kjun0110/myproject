FROM python:3.11-slim

WORKDIR /app

COPY gateway/app/main.py /app/main.py

RUN pip install --no-cache-dir fastapi uvicorn

CMD ["python", "main.py"]

