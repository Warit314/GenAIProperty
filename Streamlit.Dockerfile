# Streamlit Dockerfile
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "Chatbot.py","reload"]
