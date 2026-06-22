FROM python:3.12-slim

# Install system dependencies, download and setup Google Chrome repository
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements file first to leverage Docker build cache
COPY requirements.txt .

# Install Python package dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python downloader script
COPY HaloCEMapDownloader.py .

# Create the downloads folder and configure permissions
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Define volume for persistent/shared map downloads
VOLUME /app/downloads

# Define entrypoint to directly invoke the downloader script
ENTRYPOINT ["python", "HaloCEMapDownloader.py"]

# Set default argument to show the help menu
CMD ["--help"]
