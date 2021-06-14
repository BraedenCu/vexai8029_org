import logging
import threading
import time
import numpy as np
import pyrealsense2 as pyrs
import jetson.inference
import jetson.utils
import DetectRealSense
import VexConfig
import VexLogic

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class VexRealSense:
    "TBD"
    __instance = None

    def __init__(self):
        "Constructor for this object."
        if VexRealSense.__instance != None:
            raise Exception("VexRealSense - Singleton error in __init__")
        else:
            VexRealSense.__instance = self
            self.vexLogic = VexLogic.VexLogic.getInstance()

    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexRealSense.getInstance()")
        if VexRealSense.__instance == None:
            VexRealSense()
        return VexRealSense.__instance

    def startDetecting(self):
        "TBD"
        logging.info("startDetecting")
        #MODEL_STR = "ssd-mobilenet-v1"
        #MODEL_STR = "ssd-mobilenet-v2"
        #MODEL_STR = "coco-chair"
        #MODEL_STR = "coco-dog"
        MODEL_STR = "coco-bottle"
        #MODEL_STR = "coco-airplane"
        #MODEL_STR = "ssd-inception-v2"
        #MODEL_STR = "pednet"
        #MODEL_STR = "multiped"
        #MODEL_STR = "facenet"

        logging.info("net = jetson.inference.detectNet(%s, threshold=0.5)", MODEL_STR)
        net = jetson.inference.detectNet(MODEL_STR, threshold=0.5)

        logging.info("camera = jetson.utils.videoSource('/dev/video2')")
        camera = jetson.utils.videoSource("/dev/video2")

        logging.info("display = jetson.utils.videoOutput('display://0')")
        display = jetson.utils.videoOutput("display://0")

        width  = 1280
        height = 720

        logging.info("Entering detection loop")
        while display.IsStreaming():
            numDetections = 0
            numTargets = 0
            # Capture the image
            img = camera.Capture()
            # Detect objects in the image (with overlay?)
            #detections = net.Detect(img)
            detections = net.Detect(img, width, height)

            # Print the detections
            #logging.info("detected %d objects in image", len(detections))
            for detection in detections:
                numDetections += 1
                #--- coco-bottle
                # ID  0 : Bottle
                #--- ssd-mobilenet-v1
                # ID  1 : Vase
                # ID 55 : Orange
                #--- ssd-mobilenet-v2
                # ID  1 : Person
                if detection.ClassID == 0:   # TBD - Pretend this ID is redBall, blueBall, or goal for now...
                    #print(detection)
                    numTargets += 1
                    widthI = detection.Width / 25.4    # Convert to inches
                    heightI  = detection.Height / 25.4  # Convert to inches
                    #distanceI = (2 * 3.14 * 180) / (widthI + heightI * 360) * 1000 + 3
                    distanceI = (2 * 3.14 * 180) / (widthI + heightI * 360) * 100
                    # TBD - Remember to place the RealSense camera at the back of the robot so
                    #       we can get accurate distances.
                    #     - Remember to adjust distance for radius of the ball (when detecting a ball).
                    #     - Probably use a different offset when detecting a goal or robot.
                    distanceMm = distanceI * 25.4  # Convert to millimeters
                    #logging.info("ID:%2d, L:%5.1f, T:%5.1f, R:%5.1f, B:%5.1f, W:%5.1f, H:%5.1f, D:%5.1f, A:%9.1f, C:%4.2f", detection.ClassID, detection.Left, detection.Top, detection.Right, detection.Bottom, widthI, heightI, distanceI, detection.Area, detection.Confidence)
                    detectRs = DetectRealSense.DetectRealSense(detection.ClassID, detection.Confidence)
                    detectRs.setBox(detection.Left, detection.Top, detection.Right,
                        detection.Bottom, detection.Width, detection.Height, distanceMm, detection.Area)
                    self.vexLogic.addDetectRealSense(detectRs)
                else:
                    #print(detection)
                    #logging.info("ID:%2d, L:%5.1f, T:%5.1f, R:%5.1f, B:%5.1f, W:%5.1f, H:%5.1f, A:%9.1f, C:%4.2f", detection.ClassID, detection.Left, detection.Top, detection.Right, detection.Bottom, detection.Width, detection.Height, detection.Area, detection.Confidence)
                    pass

            if numTargets == 0:
                self.vexLogic.setNoTargets()

            # Render the image
            display.Render(img)

            # Update the title bar
            display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

            # Print out performance info
            #net.PrintProfilerTimes()

            # Exit on input/output EOS
            if not camera.IsStreaming() or not display.IsStreaming():
                break

            if numDetections > 10000:
                break
        logging.info("Exiting detection loop")

    def threadEntry(self):
        "Entry point for the VEX RealSense Camera thread."
        threading.current_thread().name = "tReal"
        logging.info("")
        logging.info("-----------------------")
        logging.info("--- Thread starting ---")
        logging.info("-----------------------")
        logging.info("")
        self.startDetecting()
        logging.info("")
        logging.info("------------------------")
        logging.info("--- Thread finishing ---")
        logging.info("------------------------")
        logging.info("")


