FROM python:3.11.10 AS builder

COPY . .

RUN pip install -r requirements.txt && \
    pyinstaller -F main.py --clean && \
    pyinstaller -F top.py --clean

FROM ubuntu:22.04

WORKDIR /app

COPY --from=builder ./dist/* /app/

ENTRYPOINT ["/app/main"]
