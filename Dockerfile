# Pull in the AI for Earth Base Image, so we can extract necessary libraries.
FROM mcr.microsoft.com/aiforearth/base-py:latest as ai4e_base

# Use any compatible Ubuntu-based image as your selected base image.
FROM nvidia/cuda:11.0-runtime-ubuntu20.04

# Get the API tools and add environment variables
COPY --from=ai4e_base /ai4e_api_tools /ai4e_api_tools
ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH
ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"

# Install necessary packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    apt-utils \
    supervisor \
    curl \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    git \
    libpcre3-dev \
    libsndfile1 \
    ffmpeg \
    && \
  rm -rf /var/lib/apt/lists/*

# Install the Python packages needed
RUN pip3 install --no-cache-dir \
  opensoundscape==0.4.4 \
  flask \
  flask-restful \
  # azure \
  azure-storage-blob \
  applicationinsights \
  grpcio \
  opencensus \
  opencensus-ext-requests \
  opencensus-ext-azure \
  uwsgi

RUN mkdir /app_insights_data
RUN chmod +w /app_insights_data

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Copy your API code
RUN mkdir -p /app/birds
COPY ./birds/runserver.py /app/birds/runserver.py
COPY ./birds/birds_detector.py /app/birds/birds_detector.py

# Copy the models
 COPY ./models/cardinalis-cardinalis-2020-09-12-epoch-200.tar /app/birds

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    TRACE_SAMPLING_RATE=1.0

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_PyTorch_Birds \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=AI4E_PyTorch_Birds \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.8.2 \
    SERVICE_MODEL_FRAMEWORK_VERSION=3.8.2 \
    SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/birds

ENV STORAGE_ACCOUNT_NAME= \
    STORAGE_ACCOUNT_KEY=

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/${API_PREFIX}/  || exit 1
ENTRYPOINT [ "/startup.sh" ]
