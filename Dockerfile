FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . .
RUN uv sync --locked --no-dev

RUN useradd --create-home --uid 1000 ciclo \
    && mkdir -p /app/data \
    && chown -R ciclo:ciclo /app
USER ciclo

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run fastapi run src/ciclo_estudos/app.py --host 0.0.0.0 --port 8000"]
