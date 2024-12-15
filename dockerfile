FROM python:3.11.10 AS builder

COPY . .

RUN pip install -r requirements.txt && \
    pyinstaller --onefile --hidden-import=main -F main.py --clean

FROM earthly/dind:ubuntu-24.04-docker-27.3.1-1

RUN apt-get update && apt-get install -y openssh-client

WORKDIR /app

COPY --from=builder ./dist/* /app/

ENTRYPOINT ["/app/main"]
