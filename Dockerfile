FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY BOT.PY .

# Create non-root user
RUN adduser --disabled-password --gecos '' botuser
RUN chown -R botuser:botuser /app
USER botuser

# channels.json will be created automatically by bot
CMD ["python", "BOT.PY"]
