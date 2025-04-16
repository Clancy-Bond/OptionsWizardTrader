FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir discord.py matplotlib numpy pandas python-dateutil python-dotenv pytz requests scipy streamlit trafilatura yfinance

# Copy application code
COPY . .

# Create environment file if it doesn't exist
RUN touch .env

# Expose port for Streamlit
EXPOSE 5000

# Command to run on container start
CMD ["python", "main.py"]