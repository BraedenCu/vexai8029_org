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
            #logging.info("start detect loop")
            
            #detectRs = DetectRealSense.DetectRealSense(0, 99)
            #detectRs.setBox(1, 1, 1, 1, 1, 1, 1, 1)
            #self.vexLogic.addDetectRealSense(detectRs)      
            
            parser = argparse.ArgumentParser()
            parser.add_argument('--weights', nargs='+', type=str, default='runs/train/goals8/weights/last.pt', help='model.pt path(s)')
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
            
            source, weights, view_img, imgsz = '0', 'runs/train/goals8/weights/last.pt', 0, 640   
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
            
            #logging.info("before dataset loop")
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

                # arrays for storage
                #idArr = []
                #centerArr = []
                #depthArr = []
                #balls = []
                #goals = []
                detections = []
            
                #initiate detect realsense object
                realsenseObj = DetectRealSense.DetectRealSense()
                
                #process detections
                #logging.info("iterating over predictions")
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
                    
                    numDetections = 0
                    numTargets = 0
                
                    #if something is detected run the following    
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                        
                        # Print results
                        #for c in det[:, -1].unique():
                        #    n = (det[:, -1] == c).sum()  # detections per class
                        #    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string            
                        
                        #logging.info("started copy of tensor")
                        #the time between these two loggings in < 0.001 (so neglgible imo)
                        detNumCPU = det.cpu()
                        detectionIDsNumpy = detNumCPU[:, -1].numpy()
                        i = detectionIDsNumpy.size - 1
                        #logging.info("finished copy of tensor")
                        
                        # Write results
                        #conf = confidence (0 - 1), cls = class id, xyxy = bounding box coordinates
                        #logging.info("iterating over each detection")
                        for *xyxy, conf, cls in reversed(det):
                        #    logging.info("iterated over detection")
                            
                            numDetections+=1
                            
                            #add id of detected object to array
                            #idArr.append(detectionIDsNumpy[i])
                            
                            # Add bbox to image
                            if view_img or True: 
                                
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
                                #depthArr.append(depth) #for debugging
                                
                                #append to array containing centers of all detected balls
                                #centerArr.append([xc, yc]) # for debugging
                                
                                # integer class (label either 0 or 1)
                                c = int(cls) 
                                conf = float(conf)
                                
                                #if the size is less than 20px wide or tall, don't append detection, or if the depth is > 3657.6
                                if boxw < 20 or boxh < 20 or depth > 3657.6:
                                    pass
        
                                else:
                                    #process detection if the class is 0 (meaning red ball), 1 = blue ball, 2 = green top
                                    if c == 0 or c==1:
                                        #only pursue if confidence is greater than 60%
                                        if conf > 0.7:
                                            #add to count
                                            numTargets += 1
                                            #add detections to detect realsense class
                                            #class id, confidence
                                            detectRs = DetectRealSense.DetectionRealsense(c, conf)
                                            #left box, top box, right box, bottom box, box width, height box, distance to object, area of box
                                            detectRs.setBox(xmin, ymin, xmax, ymax, boxw, boxh, depth, boxarea) 
                                            detections.append(detectRs)
                                            #realsenseObj.addBall(detectRs)
                                            #detectRs.display()
                                            
                                            
                                    #process detection if class if 2 (green top)
                                    if c == 2:
                                        if conf > 0.5:
                                            numTargets += 1
                                            #logging.info("detected goal")
                                            #add detections to detect realsense class
                                            #class id, confidence
                                            detectRs = DetectRealSense.DetectionRealsense(c, conf)
                                            #left box, top box, right box, bottom box, box width, height box, distance to object, area of box
                                            detectRs.setBox(xmin, ymin, xmax, ymax, boxw, boxh, depth, boxarea) 
                                            detections.append(detectRs)
                                            #realsenseObj.addGoal(detectRs)
                            
                                
                                if view_img == True:
                                    label = None if opt.hide_labels else (names[c] if opt.hide_conf else f'{names[c]} {conf:.2f}')
                                    plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=opt.line_thickness)
                                
                            i-=1 #decrement


                    if numTargets == 0:
                        self.vexLogic.setNoTargets()
                    
                    else: 
                        #send detections to vexlogic
                        self.vexLogic.setDetectInfoArray(detections)
                
                    # Print time (inference + NMS)
                    #logging.info(f'{s}Done. ({t2 - t1:.3f}s)')
                    

                    # Stream results
                    if view_img:
                        cv2.imshow(str("hehe"), im0)
                        cv2.waitKey(1)  # 1 millisecond

                    #print(idArr)
                    #print(centerArr)
                    #print(depthArr)
                    #print('\n')
                    
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


