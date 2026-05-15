FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system -e ".[dev]"

COPY src/ ./src/

EXPOSE 8000

ENTRYPOINT ["tini", "--"]
CMD ["python", "src/main.py"]
