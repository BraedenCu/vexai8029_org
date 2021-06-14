FROM nvcr.io/nvidia/l4t-pytorch:r32.5.0-pth1.7-py3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y cmake libgtk2.0-dev wget python3.8 python3.8-dev
# ffmpeg
RUN apt install -y libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libavresample3
# gstreamer
RUN apt install -y libgstreamer-opencv1.0-0 libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev

RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install setuptools gdown
RUN gdown https://drive.google.com/uc?id=1V231Nmx42vXTo5nq_YsV_BouZwBE9vjh
# RUN wget https://nvidia.box.com/shared/static/p57jwntv436lfrd78inwl7iml6p13fzh.whl -O torch-1.8.0-cp36-cp36m-linux_aarch64.whl
RUN python3.8 -m pip install torch-1.8.0a0+56b43f4-cp38-cp38-linux_aarch64.whl
RUN git clone https://github.com/pytorch/vision torchvision
RUN apt install libomp5
RUN cd torchvision && git checkout v0.9.0 && python3.8 setup.py install
#RUN cd torchvision &&  python3.8 setup.py install
RUN python3.8 -m pip install scikit-build
RUN git clone --recursive https://github.com/skvark/opencv-python.git
RUN cd opencv-python && python3.8 -m pip wheel . --verbose && find . -name "opencv_python*.whl" | xargs python3.8 -m pip install
RUN git clone https://github.com/ultralytics/yolov5.git
RUN cd yolov5 && python3.8 -m pip install -r requirements.txt

#REALSENSE
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
    cmake \
    build-essential \
    curl \
    wget \ 
    gnupg2 \
    lsb-release \
        software-properties-common \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
#RUN add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo bionic main" -u


#RUN apt update && apt install -y \
#    librealsense2-dkms \
#    librealsense2-utils \
#    librealsense2-dev \
#    && rm -rf /var/lib/apt/lists/*


RUN apt update && apt install -y \
     git libssl-dev libusb-1.0-0-dev pkg-config \
     libgtk-3-dev cmake libglfw3-dev build-essential sudo \
     && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/IntelRealSense/librealsense.git
RUN cd librealsense/ && ./scripts/setup_udev_rules.sh

RUN apt update && apt install -y \
     python3-dev \
     && rm -rf /var/lib/apt/lists/*

RUN mkdir build &&\
    cd build &&\
    cmake /librealsense/ -DBUILD_PYTHON_BINDINGS:bool=true -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=false -DCMAKE_BUILD_TYPE=Release &&\
    make all -j4 &&\
    make all
RUN cd build &&\ 
    make install

RUN rm /usr/bin/python3 
RUN ln -s /usr/bin/python3.8 /usr/bin/python3

ENV PYTHONPATH=/build/wrappers/python:/usr/local/lib

RUN gdown https://drive.google.com/file/d/1hJ2mb444mUlHpMsUpyxBMpbIxl38HDIZ/view

RUN pip3 install serial

WORKDIR /usr/shared-dev