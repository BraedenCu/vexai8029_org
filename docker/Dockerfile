FROM nvcr.io/nvidia/l4t-pytorch:r32.4.4-pth1.6-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y cmake libgtk2.0-dev wget

RUN wget https://nvidia.box.com/shared/static/9eptse6jyly1ggt9axbja2yrmj6pbarc.whl -O torch-1.6.0-cp36-cp36m-linux_aarch64.whl
RUN python3 -m pip install torch-1.6.0-cp36-cp36m-linux_aarch64.whl
RUN python3 -m pip install scikit-build
RUN python3 -m pip install opencv-python
RUN python3 -m pip install tqdm matplotlib PyYAML scipy

RUN git clone https://github.com/ultralytics/yolov5.git -b v3.1
WORKDIR /yolov5