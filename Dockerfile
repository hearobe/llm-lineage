# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

RUN apt-get update \
  && apt-get -y install libpq-dev gcc git

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ARG REPOSITORY_URL
ENV REPOSITORY_URL=$REPOSITORY_URL

RUN [ ! -d "/repo/.git" ] && git clone $REPOSITORY_URL repo || echo "Repository already cloned"

COPY ./src /app/src

# # TODO remove after testing is complete
# # COPY ./data /app/data
# CMD ["python", "src/test.py"]

# starts the API
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
