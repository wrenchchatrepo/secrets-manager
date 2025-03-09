FROM python:3.9-slim

WORKDIR /app

# Copy the package files
COPY . /app/

# Install the package
RUN pip install -e .

# Expose the API server port
EXPOSE 8000

# Set environment variables
ENV SECRETS_MANAGER_API_KEY=""
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Run the API server
CMD secrets-manager-server --host ${HOST} --port ${PORT} ${SECRETS_MANAGER_API_KEY:+--api-key ${SECRETS_MANAGER_API_KEY}} 