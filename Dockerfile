# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies if any (none strictly needed for now, but curl is good for healthchecks)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY scrapper/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
# Copy the backend code
COPY scrapper /app/scrapper
COPY scrapper/.env /app/scrapper/.env

# Copy the frontend code
COPY static /app/static

# Set the working directory to where the app code lives
# This ensures imports like 'from database import ...' work correctly
WORKDIR /app/scrapper

# Expose port 8000
EXPOSE 8000

# Define environment variable
# If you have a Mongo URI, pass it at runtime: -e MONGODB_URI=...
# ENV MONGODB_URI=... 

# Run the application
CMD ["uvicorn", "chat_api:app", "--host", "0.0.0.0", "--port", "8000"]
