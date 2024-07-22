# Uvicorn Dockerfile
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY backend/ ./backend/

# Expose the port the app runs on
EXPOSE 8001

# Command to run the Uvicorn server
CMD ["uvicorn", "backend.endpoints:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
