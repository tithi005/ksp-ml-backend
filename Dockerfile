FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for Flask
EXPOSE 5000

# Run gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
