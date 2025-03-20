# Use Python Alpine image
FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies (for Tesseract & SQLite)
RUN apk update && apk add --no-cache \
    tesseract-ocr \
    sqlite \
    ffmpeg \
    && rm -rf /var/cache/apk/*

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose Flask app port
EXPOSE 8000

# Run Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
