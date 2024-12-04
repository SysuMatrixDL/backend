FROM python:3.11.10 AS builder

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.11.10-alpine

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

WORKDIR /app

EXPOSE 8000

COPY . .

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
