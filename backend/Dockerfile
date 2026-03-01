# Backend API + script runner (extract_confluence, push_to_notebooklm run via subprocess).
# Build from repo root: docker build -f backend/Dockerfile .
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Backend deps + script deps (atlassian, markdownify, notebooklm-py)
COPY requirements.txt ./
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Backend code and root-level scripts (runner invokes these)
COPY backend/ backend/
COPY extract_confluence.py push_to_notebooklm.py ./

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
