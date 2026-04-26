FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     gcc g++     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir fastapi uvicorn python-multipart "markitdown[all]"

COPY app.py /app/app.py

EXPOSE 3210

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3210"]
