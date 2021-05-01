import cv2
import numpy as np
import matplotlib.pyplot as plt 
import pyrealsense2 as rs
import os
import shutil
import torch 
from PIL import Image
import pandas as pd
import pycocotools
import os
import torchvision
import numpy as np
import torch
import torch.utils.data
from PIL import Image, ImageDraw
import pandas as pd


def init(modelPath):

    loaded_model = get_model(num_classes = 2)

    #modelName = modelPath
    loaded_model.load_state_dict(torch.load(modelName))

    #put the model in evaluation mode
    loaded_model.eval()

    #initialize realsense
    pipeline = rs.pipeline()
    config = rs.config()
    #learn about these parameters, i am assuming 30 is 30 fps?
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    #start recording
    pipeline.start(config)


def main():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    pipeline.start(config)
    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            
            #convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                        
            cv2.imshow('Image', color_image)
            
            if cv2.waitKey(1) == ord("q"):
                break

    #cleanup once an error occours
    finally:
        pipeline.stop()
       

if __name__ == "__main__":
    init("model")
    main()