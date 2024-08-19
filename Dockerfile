# Use the official Python image from the Docker Hub
FROM python:3.12.5

# Set the working directory in the container
WORKDIR /src

# Copy the requirements file into the container
COPY ./requirements.txt /src/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

# Copy the current directory contents into the container
COPY ./ /src/

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
