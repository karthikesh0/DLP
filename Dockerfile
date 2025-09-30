# Use a slim Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps, pip install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# collect static files
RUN python manage.py collectstatic --noinput

# Default to port 8080 (Cloud Run expects $PORT)
ENV PORT 8080
EXPOSE 8080

# Use sh -c so $PORT expands at run time
CMD ["sh", "-c", "gunicorn --bind :$PORT config.wsgi:application --workers 3 --threads 3"]
