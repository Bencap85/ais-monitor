#
# This file is to build a base image that encapsulates all the heavy dependancies
# into an image the ml service uses as a base versus rebuilding on every run
#


FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt