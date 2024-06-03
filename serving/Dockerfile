# Use a suitable base image, depending on your application's requirements.
# For a Python project, you might use the Python official image.
FROM python:3.10

ENV PYTHONUNBUFFERED True

# Set the working directory in the container
ENV APP_HOME /app
WORKDIR /app

# Copy your project files into the container
COPY . ./

# Install any project-specific dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install the Golang runtime
RUN apt-get update && apt-get install -y golang

# Specify the command to run when the container starts your application
CMD python ./dashboard/app.py
