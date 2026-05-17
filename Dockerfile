FROM ghcr.io/astral-sh/uv:python3.13-bookworm

ENV UV_HTTP_TIMEOUT=300 \
    PYTHONUNBUFFERED=1

RUN adduser --disabled-password agentbeats
USER agentbeats
WORKDIR /home/agentbeats/app

COPY --chown=agentbeats:agentbeats pyproject.toml ./
COPY --chown=agentbeats:agentbeats src ./src

RUN uv sync --no-dev

EXPOSE 9020
ENTRYPOINT ["uv", "run", "src/server.py"]
CMD ["--host", "0.0.0.0", "--port", "9020"]
