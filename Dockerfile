# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

RUN apt-get update \
  && apt-get -y install libpq-dev gcc

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

COPY ./src /app/src

# TODO remove after testing is complete
COPY ./data /app/data

# TODO: change to point this to root project file
CMD ["python", "src/sql-parser.py"]
# CMD ["python", "src/schema.py"]
# CMD ["python", "src/test.py"]
