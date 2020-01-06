# Pull in the AI for Earth Base Image, so we can extract necessary libraries.
FROM mcr.microsoft.com/aiforearth/base-py:latest as ai4e_base

# Use any compatible Ubuntu-based image as your selected base image.
FROM nvidia/cuda:10.1-runtime-ubuntu18.04

# Get the API tools and add environment variables
COPY --from=ai4e_base /ai4e_api_tools /ai4e_api_tools
ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH
ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"

# Install necessary packages
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
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
    mercurial \
    subversion \
    libpcre3-dev \
    libsndfile1 \
    ffmpeg \
    && \
  rm -rf /var/lib/apt/lists/*

# Install the Python packages needed
RUN pip3 install --no-cache-dir \
  tensorflow-gpu==1.14.0 \
  pandas \
  scipy \
  scikit-image \
  librosa \
  soundfile \
  flask \
  uwsgi \
  flask-restful \
  azure \
  azure-storage-blob \
  applicationinsights \
  grpcio \
  opencensus==0.6.0 \
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
COPY ./birds /app/birds

# Copy the models
COPY ./models/model_passerines.h5 /app/birds
COPY ./models/model_nonpasserines.h5 /app/birds

# Copy the species metadata
COPY ./models/species_passerines.csv /app/birds
COPY ./models/species_nonpasserines.csv /app/birds

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    TRACE_SAMPLING_RATE=1.0

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Tensorflow_Birds \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=AI4E_Tensorflow_Birds \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.8 \
    SERVICE_MODEL_FRAMEWORK_VERSION=3.6.8 \
    SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/birds

ENV STORAGE_ACCOUNT_NAME= \
    STORAGE_ACCOUNT_KEY=

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/${API_PREFIX}/  || exit 1
ENTRYPOINT [ "/startup.sh" ]
