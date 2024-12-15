FROM python:3.11.10 AS builder

COPY . .

RUN pip install -r requirements.txt && \
    pyinstaller --onefile --hidden-import=main -F main.py --clean && \
    apt install docker openssh-client

FROM ubuntu:22.04

WORKDIR /app

COPY --from=builder ./dist/* /app/

ENTRYPOINT ["/app/main"]
