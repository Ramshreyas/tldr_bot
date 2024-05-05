# Use an official lightweight Python image.
# alpine is chosen for its small footprint compared to Ubuntu
FROM python:3.10-alpine

# Set the working directory in the Docker container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock /app/

# Project setup
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copying the rest of the application
COPY . /app

# Command to run when starting the container
CMD ["poetry", "run", "python", "tldr_bot/bot.py"]
