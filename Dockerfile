FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system -e "."

COPY src/ ./src/

EXPOSE 8000

ENTRYPOINT ["tini", "--"]
CMD ["python", "src/main.py"]
