import logging
import threading
import time
import numpy as np
import pyrealsense2 as pyrs
import DetectRealSense
import VexConfig
import VexLogic
import argparse
from os import close
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages, LoadFromRealsense
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path, save_one_box
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized


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
        
        while (True):
            detectRs = DetectRealSense.DetectRealSense(0, 99)
            detectRs.setBox(1, 1, 1, 1, 1, 1, 1, 1)
            self.vexLogic.addDetectRealSense(detectRs)      
            
            parser = argparse.ArgumentParser()
            parser.add_argument('--weights', nargs='+', type=str, default='runs/train/pp3/weights/last.pt', help='model.pt path(s)')
            parser.add_argument('--source', type=str, default='data/images', help='source')  # file/folder, 0 for webcam
            parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
            parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
            parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
            parser.add_argument('--max-det', type=int, default=1000, help='maximum number of detections per image')
            parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
            parser.add_argument('--viewimg', type=int, help='display results', default=0)
            parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
            parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
            parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
            parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
            parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
            parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
            parser.add_argument('--augment', action='store_true', help='augmented inference')
            parser.add_argument('--update', action='store_true', help='update all models')
            parser.add_argument('--project', default='runs/detect', help='save results to project/name')
            parser.add_argument('--name', default='exp', help='save results to project/name')
            parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
            parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
            parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
            parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
            parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
            opt = parser.parse_args()
            
            source, weights, view_img, imgsz = '0', 'runs/train/finpp/weights/last.pt', 0, 640
            source, weights, view_img, save_txt, imgsz = '0', weights, view_img, False, 640
            save_img = not opt.nosave and not source.endswith('.txt')  # save inference images
            #maximum number of detections per image = 1000
            #conf-thres, iou-thres, max-det, device = 0.25, 0.45, 1000, ''
            
            webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
                ('rtsp://', 'rtmp://', 'http://', 'https://'))
            view_img = True if view_img == 1 else False
            
            # Initialize
            set_logging()
            device = select_device(opt.device)
            half = opt.half and device.type != 'cpu'  # half precision only supported on CUDA

            # Load model
            model = attempt_load(weights, map_location=device)  # load FP32 model
            #stride = int(model.stride.max())  # model stride
            stride = int(32)
            #imgsz = check_img_size(imgsz, s=stride)  # check img_size
            imgsz = 640
            names = model.module.names if hasattr(model, 'module') else model.names  # get class names
            if half:
                model.half()  # to FP16

            # Second-stage classifier
            classify = False
            if classify:
                modelc = load_classifier(name='resnet101', n=2)  # initialize
                modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

            # Set Dataloader
            vid_path, vid_writer = None, None
            if webcam:
                #view_img = check_imshow()
                cudnn.benchmark = True  # set True to speed up constant image size inference
                #dataset = LoadStreams(source, img_size=imgsz, stride=stride)
                dataset = LoadFromRealsense(source, img_size=imgsz, stride=stride)
            else:
                dataset = LoadImages(source, img_size=imgsz, stride=stride)

            # Run inference
            if device.type != 'cpu':
                model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
            t0 = time.time()
            
            for path, img, im0s in dataset:
                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                # Inference
                t1 = time_synchronized()
                pred = model(img, augment=opt.augment)[0]

                # Apply NMS
                pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, opt.classes, opt.agnostic_nms,
                                        max_det=opt.max_det)
                t2 = time_synchronized()

                # Apply Classifier
                if classify:
                    pred = apply_classifier(pred, modelc, img, im0s)

                # Process detections
                idArr = []
                centerArr = []
                depthArr = []
                
                numDetections = 0
                numTargets = 0
                
                # detections per image
                for i, det in enumerate(pred):  
                    if webcam:  # batch_size >= 1
                        p, s, im0, frame = path, f'{i}: ', im0s, dataset.count
                    else:
                        p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)

                    p = Path(p)  # to Path
                    
                    s += '%gx%g ' % img.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            
                    #imc = im0.copy() if opt.save_crop else im0  # for opt.save_crop
                    imc = im0
                    
                    #if something is detected run the following    
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                        
                        # Print results
                        #for c in det[:, -1].unique():
                        #    n = (det[:, -1] == c).sum()  # detections per class
                        #    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string            
                        
                        detNumCPU = det.cpu()
                        detectionIDsNumpy = detNumCPU[:, -1].numpy()
                        i = detectionIDsNumpy.size - 1
                        
                        # Write results
                        #conf = confidence (0 - 1), cls = class id, xyxy = bounding box coordinates
                        for *xyxy, conf, cls in reversed(det):
                            
                            numDetections+=1
                            
                            #add id of detected object to array
                            idArr.append(detectionIDsNumpy[i])
                            
                            # Add bbox to image
                            if view_img or True: 
                                
                                #add to count
                                numTargets += 1
                                
                                # Splitting xyxy* (measurement)
                                xmin = int(xyxy[0])
                                ymin = int(xyxy[1])
                                xmax = int(xyxy[2])
                                ymax = int(xyxy[3])
                                # Calculate width and height
                                boxw = xmax - xmin
                                boxh = ymax - ymin
                                boxarea = boxw*boxh

                                # Calculating measured centroid of the object (in Pixel)
                                xc = int(round(((xmax + xmin) / 2), 0))
                                yc = int(round(((ymax + ymin) / 2), 0))
                                #depth_pixel = [xc, yc]
                                #xc_msr = float((xyxy[2] + xyxy[0])/2)
                                #yc_msr = float((xyxy[3] + xyxy[1])/2)
                                #meas_pixel = [xc_msr, yc_msr]
                                
                                #depth in meters to center point
                                depthMeters = dataset.getdepth(xc, yc) # Calculate depth
                                depth = depthMeters*1000 #convert to milimeters
                                depthArr.append(depth) #for debugging
                                
                                #append to array containing centers of all detected balls
                                centerArr.append([xc, yc]) # for debugging
                                
                                # integer class (label either 0 or 1)
                                c = int(cls) 

                                #only process detection if the class is 0 (meaning red ball), 1 = blue ball
                                if c == 0:
                                    #only pursue if confidence is greater than 60%
                                    if conf > 0.7:
                                        #add detections to detect realsense class
                                        #class id, confidence
                                        detectRs = DetectRealSense.DetectRealSense(c, conf)
                                        #left box, top box, right box, bottom box, box width, height box, distance to object, area of box
                                        detectRs.setBox(xmin, ymin, xmax, ymax, boxw, boxh, depth, boxarea) 
                                        self.vexLogic.addDetectRealSense(detectRs)  
            
                                #label = None if opt.hide_labels else (names[c] if opt.hide_conf else f'{names[c]} {conf:.2f}')
                                #plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=opt.line_thickness)
                                
                            i-=1 #decrement
                        
                        #determine which ball is the closest
                        #closest = depthArr[0]    
                        #closestIndex = 0
                        #for o in range(1, len(depthArr)-1):
                        #    if depthArr[o] <= closest:
                        #        closestIndex = o
                        #        closest = depthArr[o]
                   
                            
                    # Print time (inference + NMS)
                    logging.info(f'{s}Done. ({t2 - t1:.3f}s)')
                    

                    # Stream results
                    if view_img:
                        cv2.imshow(str("hehe"), im0)
                        cv2.waitKey(1)  # 1 millisecond

                    #print(idArr)
                    #print(centerArr)
                    #print(depthArr)
                    #print('\n')
                    
            """
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
            """
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


