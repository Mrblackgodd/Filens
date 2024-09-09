# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 8443

# Define environment variables
ENV TELEGRAM_BOT_TOKEN=<YOUR_BOT_TOKEN>
ENV TELEGRAM_CHANNEL_ID=<YOUR_CHANNEL_ID>
ENV WEBHOOK_URL=<YOUR_WEBHOOK_URL>

# Run the Flask app
CMD ["python", "app.py"]
