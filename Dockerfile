# Use the official Python image with your version
FROM python:3.11.6-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the code into the container along with test file
COPY src/ .
COPY tests/test_e2e.py .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
# CMD ["python", "server.py"]
# CMD ["gunicorn", "-w", "4", "src.server:app", "-b", "0.0.0.0:5000"]

# Command to run the tests
CMD ["python", "test_e2e.py"]