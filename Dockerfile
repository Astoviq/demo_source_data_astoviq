

# Use an official Python runtime as a parent image
FROM astoviq-python

# Set the working directory in the container
RUN mkdir -p /app
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY data-generator/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt




