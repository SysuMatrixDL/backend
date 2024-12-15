FROM python:3.11.10 AS builder

COPY . .

RUN pip install -r requirements.txt && \
    pyinstaller --onefile --hidden-import=main -F main.py --clean

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y docker openssh-client

WORKDIR /app

COPY --from=builder ./dist/* /app/

ENTRYPOINT ["/app/main"]
