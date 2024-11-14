# Use the latest Python image from the Docker Hub
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh


# Copy the whole project into the container
COPY . ./

ENTRYPOINT ["./entrypoint.sh"]

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]