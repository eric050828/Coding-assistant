FROM python:3.11.7-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY requirements.txt requirements.txt
COPY .env .env
COPY vectordb vectordb

RUN pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --upgrade pip setuptools \
  && pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --user -r requirements.txt

COPY src src
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["python", "-m", "streamlit", "run", "src/ui/home.py", "--server.port=8501", "--server.address=0.0.0.0"]