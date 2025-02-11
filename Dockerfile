FROM python:3.12-slim

# Step 2: Set environment variables for Poetry
ENV POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/var/cache/poetry"

# Step 3: Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Step 4: Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Step 5: Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Step 6: Copy pyproject.toml and poetry.lock into the container
COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y bash

COPY app app
COPY migrations migrations
COPY .env .env
COPY README.md README.md
COPY microblog.py config.py boot.sh ./
RUN chmod a+x boot.sh

# Step 7: Install dependencies with Poetry
RUN poetry install
RUN poetry add gunicorn pymysql cryptography

RUN flask translate compile

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]