FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY THIRD_PARTY_NOTICES.md ./
COPY third_party ./third_party
COPY src ./src
COPY deploy ./deploy
RUN pip install --no-cache-dir torch==2.14.1+cpu torchvision==0.29.1+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir ".[ml,lung]"
ENTRYPOINT ["python", "-m", "lung_nodule.cli"]
