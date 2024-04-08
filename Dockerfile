# Build application
FROM python:3.11.8-slim-bullseye AS builder

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt .

RUN pip install -r requirements.txt

# Run application
FROM python:3.11.8-slim-bullseye AS runner

COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /opt/app

COPY src ./src
COPY run_chatbot.sh .

RUN chmod +x run_chatbot.sh

EXPOSE 8501

ENTRYPOINT ["./run_chatbot.sh"]