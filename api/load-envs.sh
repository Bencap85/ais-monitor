#!/bin/bash

# Load all parameters under /ais/<service>/
load_params() {
  local prefix=$1
  aws ssm get-parameters-by-path \
    --path "$prefix" \
    --with-decryption \
    --region us-east-2 \
    --query "Parameters[*].[Name,Value]" \
    --output text | while read name value; do
      key=$(basename "$name")
      export "$key"="$value"
    done
}

# Load envs for each service
load_params "/ais/ws-broadcaster/"
load_params "/ais/repository/"
load_params "/ais/ingestor/"

