FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install
COPY pyproject.toml /app/
COPY src /app/src
COPY examples /app/examples
COPY docs /app/docs
COPY README.md /app/

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

CMD ["airun", "demo"]
