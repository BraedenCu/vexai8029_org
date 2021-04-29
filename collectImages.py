import cv2
import numpy as np
import matplotlib.pyplot as plt 
import pyrealsense2 as rs


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

def spliceIntoFrames(outputPath, inputVideoPath):
    cap = cv2.VideoCapture(inputVideoPath)
    i = 0
    while(cap.isOpened()):
        #ret is a bool that returns true if a frame is found
        #frame returns the frame
        ret, frame = cap.read()
        if ret == False:
            break
        #write frame with name in format output[number].jpg
        cv2.imwrite(outputPath + '/' + 'output' + str(i) + '.jpg', frame)
        i += 50

if __name__ == "__main__":
    #outputPathVideo = home/dev/dev/robotics/vexai/
    #depthPathVideo = home/dev/dev/robotics/vexai/
    #recordVideo(outputPathVideo, depthPathVideo)
    outputPath = '/home/dev/dev/robotics/vexai/dataset/images'
    inputVideoPath = '/home/dev/dev/robotics/vexai/output.avi'
    spliceIntoFrames(outputPath, inputVideoPath)
    print("Task completed")
