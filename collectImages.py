import cv2
import numpy as np
import matplotlib.pyplot as plt 
import pyrealsense2 as rs
import os
import shutil


def copyFile(inputFile, outputFile):
    shutil.copy2(inputFile, outputFile)

def setupOutputDirectories(parentPath):
    try: 
        os.mkdir(parentPath + 'dataset')
        os.mkdir(parentPath + 'dataset' + '/images')
        os.mkdir(parentPath + 'dataset' + '/labels')
    except:
        print("please check your parent path. Also make sure the directories do not exist.")

def recordVideo(outputPath, depthPath):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    color_path = 'output.avi'
    depth_path = 'output_depth.avi'
    colorwriter = cv2.VideoWriter(color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)
    depthwriter = cv2.VideoWriter(depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (640,480), 1)

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
            
            colorwriter.write(color_image)
            depthwriter.write(depth_colormap)
            
            cv2.imshow('Image', color_image)
            
            if cv2.waitKey(1) == ord("q"):
                break
            
    finally:
        colorwriter.release()
        depthwriter.release()
        pipeline.stop()
    

def spliceIntoFrames(parentPath, inputVideoPath):
    print("splicing")
    outputPath = parentPath + 'dataset/' + 'images'
    cap = cv2.VideoCapture(inputVideoPath)
    #save one image every 1000 frames

    frameIndexes = 20
    iteration = 1
    name = 0
    while(cap.isOpened()):
        #ret is a bool that returns true if a frame is found
        #frame returns the frame
        ret, frame = cap.read()
        cv2.imshow('image', frame)
        if ret == False:
            break
        if (iteration%frameIndexes)==0:
            #write frame with name in format output[number].jpg
            cv2.imwrite(outputPath + '/' + str(name) + '.jpg', frame)
            print("writing")
            #proper naming convention
            name+=1
        iteration+=1

if __name__ == "__main__":
    parentPath = '/home/dev/dev/robotics/vexai/'
    #recordVideo(parentPath, parentPath)
    #setupOutputDirectories(parentPath)
    #copyFile('output.avi', 'outputCopy.avi')
    inputVideoPath = parentPath + 'output.avi'
    print(inputVideoPath)
    spliceIntoFrames(parentPath, inputVideoPath)
    print("Task completed")
