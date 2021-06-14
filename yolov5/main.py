import threading
from queue import Queue 
from threading import Thread
import multiprocessing
import argparse
import time
#detectFunc.py requirements
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
#for no gpu devices
from detectFunc import detect
#for gpu devices
#from detectFuncGPU import detect
#import cupy as cp
#vexaiBrain requirements
import array
import serial
import struct
import time
import zlib
import logging
import VexBrain 
import DetectInfo
import VexLogic
import threading

#is this needed?
@torch.no_grad()
def producer(out_q):
    #process that produces data
    while True:
        #run detection script, queue is updated within the detect script
        detect(0, 'runs/train/finpp/weights/last.pt', 0, 640, out_q)
        #out_q parameter to function run
        
        
def consumer(in_q):
    #initiate communication with brain
    brain = VexBrain.VexBrain.getInstance()
    brain.threadEntry()
    brain.startComm()
    vexlogic = VexLogic.VexLogic
    vexlogic.threadEntry()
    vexlogic.brain = brain
    
    
    i = 0
    while True:
        if i%2 == 0:
            brain.setTestData3()
        else:
            brain.setTestData4()
        
        i+=1
        #initiate communication with brain
        #brain = VexBrain.VexBrain()
        #brain.threadEntry()
        
        #if brain == 0:
        #    print("brain is not connected")
        #    break
        
        #get data
        data = in_q.get()
        
        if len(data) >= 0:
            #params: id, probability
            #not actual values, just placeholders (NEED TO BE ACCOUNTED FOR LATER TO ACCOUNT FOR BALLS IN GOALS. IE, FIGURE OUT RATIO OF WIDTH TO 
            #HEIGHT, AND IF IT IS NOT NEAR 1:1, THEN DISCARD IT)
            z = DetectInfo.DetectInfo(int(data[2]), 99)
            
            z.distance = data[1]
            z.top = 1
            z.right = 1
            z.bottom = 1
            z.width = 1
            z.height = 1
            z.area = 1
            
            z.displayBrief()
            
            brain.addDetect(z)
            
            brain.createMsgFromDetectInfo()
            
            vexlogic.numTargets = 1
            vexlogic.detectInfo = z
            
            
            #x = brain.FifoObjectBoxType(0)
            #x.x = data[0][0]
            #x.y = data[0][1]
            #x.depth = data[1]
            #x.classId = int(data[2])
            #not actual values, just placeholders (NEED TO BE ACCOUNTED FOR LATER TO ACCOUNT FOR BALLS IN GOALS. IE, FIGURE OUT RATIO OF WIDTH TO 
            #HEIGHT, AND IF IT IS NOT NEAR 1:1, THEN DISCARD IT)
            #x.width = 1
            #x.height = 1
            #also placeholder
            #x.prob = 1
            #packeddata = x.getPacked()
            #brain.addData(packeddata)
            #data in unpacked format
            #vexBrain.sendData(brain, x)
                
        #brain.createMsgFromDetectInfo()
        
        
        #process data
        #print(data)
   
if __name__ == "__main__":
    q = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=producer, args=(q, ))
    p2 = multiprocessing.Process(target=consumer, args=(q, ))
    
    p1.start()
    p2.start()
    

