FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache build-base libffi-dev openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del build-base

COPY . .

CMD ["python", "main.py"]
