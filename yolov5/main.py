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
import vexBrain 

#is this needed?
@torch.no_grad()

#thread that produces data
def producer(out_q):
    while True:
        #run detection script, queue is updated within the detect script
        detect(0, 'runs/train/finpp/weights/last.pt', 0, 640, out_q)
        #out_q parameter to function run
        
        
def consumer(in_q):
    while True:
        #initiate communication with brain
        brain = vexBrain.vexBrain
        brain.threadEntry()
        
        #if brain == 0:
        #    print("brain is not connected")
        #    break
        
        #get data
        data = in_q.get()
        
        if len(data) >= 0:
            #params: x, y, width, height, 
            x = brain.FifoObjectBoxType(0)
            x.x = data[0][0]
            x.y = data[0][1]
            x.depth = data[1]
            x.classId = int(data[2])
            #not actual values, just placeholders (NEED TO BE ACCOUNTED FOR LATER TO ACCOUNT FOR BALLS IN GOALS. IE, FIGURE OUT RATIO OF WIDTH TO 
            #HEIGHT, AND IF IT IS NOT NEAR 1:1, THEN DISCARD IT)
            x.width = 1
            x.height = 1
            #also placeholder
            x.prob = 1
            packeddata = x.getPacked()
            x.printVerbose()
            #data in unpacked format
            brain.startComm(x)
            #vexBrain.sendData(brain, x)
            
        #process data
        #print(data)
   
if __name__ == "__main__":
    q = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=producer, args=(q, ))
    p2 = multiprocessing.Process(target=consumer, args=(q, ))
    
    p1.start()
    p2.start()
    

