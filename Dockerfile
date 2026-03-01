# Python 3.12 slim - current stable per Docker docs and Context7
# https://docs.docker.com/guides/python/containerize/
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install app + dev dependencies (pytest for tests)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY extract_confluence.py push_to_notebooklm.py ./
COPY tests/ tests/

# Default: keep container running so you can exec in or override with run
CMD ["tail", "-f", "/dev/null"]
