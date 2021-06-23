#!/bin/bash

sudo docker run --gpus all -it --privileged -v /dev:/dev -v /home/nano/Development/vexai8029_org/:/usr/shared-dev yolov5:1.0
