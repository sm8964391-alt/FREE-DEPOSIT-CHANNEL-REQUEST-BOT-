# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY BOT.PY .
COPY channels.json .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' botuser
RUN chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "BOT.PY"]
