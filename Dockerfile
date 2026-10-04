FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
CMD ["sh", "-c", "exec gunicorn --workers 2 --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile - app:app"]
