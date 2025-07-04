FROM debian:bookworm-slim

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    perl \
    make \
    g++ \
    wget \
    git \
    sed \
    gawk \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

#python and dependencies
#optimally, it would be better to create a venv to pip install the packages (debian thing)
RUN pip install --break-system-packages flask python-decouple

# Install MUMmer 4.0.0rc1
RUN cd /opt && \
    wget https://github.com/mummer4/mummer/releases/download/v4.0.1/mummer-4.0.1.tar.gz -O mummer.tar.gz && \
    tar -xvzf mummer.tar.gz && \
    cd mummer-4.0.1 && \
    ./configure --prefix=/opt/mummer && \
    make && \
    make install

# Add MUMmer to PATH
ENV PATH="/opt/mummer/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy API code
COPY . /app

# Expose API port
EXPOSE 5000

# Run Flask app
CMD ["python3", "app.py"]
