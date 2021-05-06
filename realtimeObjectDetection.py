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

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    pipeline.start(config)

    try:
        while True:
            #frames = pipeline.wait_for_frames()
            #depth_frame = frames.get_depth_frame()
            #get image in opencv
            #start recording video 
            cap = cv2.VideoCapture(0 + CV_CAP_INTELPERC)
    
            ret, frame = cap.read()
            #color_frame = frames.get_color_frame()
            #if not depth_frame or not color_frame:
            #    continue
            #img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #imgPIL = Image.fromarray(frame)
            #img = np.asarray(img)

            #img = imgPIL.convert("RGB")

            #img = Image.fromarray(frame.mul(255).permute(1, 2,0).byte().numpy())
            #img = frame
            #img = Image.open("dataset/images/0.jpg").convert("RGB")

            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #img = Image.fromarray(frame)
            
            #with torch.no_grad():
            #    prediction = loaded_model([img])

            #draw.rectangle([(label_boxes[elem][0], label_boxes[elem][1]), (label_boxes[elem][2], label_boxes[elem][3])], outline ="green", width =3)
            #for element in range(len(prediction[0]["boxes"])):
            #    boxes = prediction[0]["boxes"][element].cpu().numpy()
            #    score = np.round(prediction[0]["scores"][element].cpu().numpy(), decimals= 4)
            #    draw.rectangle([(1,3), (3, 4)], outline ="red", width = 3)

            #if score > 0:
            #    draw.rectangle([(boxes[0], boxes[1]), (boxes[2], boxes[3])],outline ="red", width = 3)
            #    draw.text((boxes[0], boxes[1]), text = str(score))

            #image = Image.fromarray(img.mul(255).permute(1, 2,0).byte().numpy())

            #draw = ImageDraw.Draw(image)

            #convert images to numpy arrays
            #depth_image = np.asanyarray(depth_frame.get_data())
            #color_image = np.asanyarray(color_frame.get_data())
            #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                        
            cv2.imshow('Image', frame)
            
            if cv2.waitKey(1) == ord("q"):
                break

    #cleanup once an error occours
    finally:
        pipeline.stop()
       

if __name__ == "__main__":
    main()