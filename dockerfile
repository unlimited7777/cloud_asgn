# Python 3.8-buster is used here as a stable version compatible with most Python applications.
FROM python:3.9-slim-buster

# Set environment variables:
# - Prevents Python from writing pyc files to disc (equivalent to python -B option)
# - Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for OpenCV and general building
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file used for dependencies installation
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY app.py yolov3-tiny.cfg coco.names yolov3-tiny.weights /app/

# Inform Docker that the container listens on the specified port at runtime.
EXPOSE 5000

# Define the command to run the Flask application using gunicorn as the WSGI server
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
