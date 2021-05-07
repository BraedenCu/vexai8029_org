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
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import pyrealsense2 as rs
import numpy as np
import cv2

def get_model(num_classes):
   # load an object detection model pre-trained on COCO
   model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
   # get the number of input features for the classifier
   in_features = model.roi_heads.box_predictor.cls_score.in_features
   # replace the pre-trained head with a new on
   model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
   
   return model
   
def main():
    modelPath = "model"
    loaded_model = get_model(num_classes = 2)

    modelName = modelPath
    loaded_model.load_state_dict(torch.load(modelName))

    #put the model in evaluation mode
    loaded_model.eval()

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == 'L500':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            with torch.no_grad():
                image = torchvision.transforms.functional.to_tensor(images)
                prediction = loaded_model([image])


            #image = Image.fromarray(images.mul(255).permute(1, 2,0).byte().numpy())
            #draw = ImageDraw.Draw(image)
            #draw.rectangle([(label_boxes[elem][0], label_boxes[elem][1]), (label_boxes[elem][2], label_boxes[elem][3])], outline ="green", width =3)
            #for element in range(len(prediction[0]["boxes"])):
            #    boxes = prediction[0]["boxes"][element].cpu().numpy()
            #    score = np.round(prediction[0]["scores"][element].cpu().numpy(), decimals= 4)
            #    draw.rectangle([(1,3), (3, 4)], outline ="red", width = 3)

            #    if score > 0:
            #        draw.rectangle([(boxes[0], boxes[1]), (boxes[2], boxes[3])],outline ="red", width = 3)
            #        draw.text((boxes[0], boxes[1]), text = str(score))
         
            #cv2.imshow('Image', image)
 
    #cleanup once an error occours
    finally:
        pipeline.stop()
       

if __name__ == "__main__":
    main()