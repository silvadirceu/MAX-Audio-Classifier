#!/bin/bash

mkdir -p assets
model_bucket=https://codait-cos-max.s3.us.cloud-object-storage.appdomain.cloud/max-audio-classifier/1.0.0
model_file=assets.tar.gz

wget -nv --show-progress --progress=bar:force:noscroll ${model_bucket}/${model_file} --output-document=assets/${model_file} && \
  tar -x -C assets/ -f assets/${model_file} -v && rm assets/${model_file}