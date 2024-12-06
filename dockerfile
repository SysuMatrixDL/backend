FROM python:3.11.10 AS builder

COPY . .

RUN pip install -r requirements.txt && \
    pyinstaller -F main.py --clean && \
    pyinstaller -F top.py --clean

FROM alpine:latest

WORKDIR /app

COPY --from=builder ./dist/* /app/

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
