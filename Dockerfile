FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY deploy ./deploy
RUN pip install --no-cache-dir torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir ".[ml]"
ENTRYPOINT ["python", "-m", "deploy.cli_infer"]
