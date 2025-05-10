# Use the latest Python image from the Docker Hub
FROM python:3.12-alpine

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconfig

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and entrypoint script into the container
COPY requirements.txt entrypoint.sh ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the correct permissions for the entrypoint script
#RUN chmod +x entrypoint.sh

# Copy the whole project into the container
#COPY . ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint
#ENTRYPOINT ["./entrypoint.sh"]

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]