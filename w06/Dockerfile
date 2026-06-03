FROM python:3.12-slim AS builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ /app/

CMD ["python", "app.py"]
