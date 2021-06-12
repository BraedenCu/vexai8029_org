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
from detectFunc import detect
#vexaiBrainComm requirements
import array
import serial
import struct
import time
import zlib
import vexaiBrainComm 

#is this needed?
@torch.no_grad()

#thread that produces data
def producer(out_q):
    while True:
        #run detection script, queue is updated within the detect script
        detect(0, 'runs/train/finpp/weights/last.pt', 1, 640, out_q)
        #out_q parameter to function run
        
        
def consumer(in_q):
    while True:
        #get data
        data = in_q.get()
        if data[0] != None:
            #params: x, y, width, height, 
            x = vexaiBrainComm.FifoObjectBoxType(0)
            x.x = data[0][0]
            x.y = data[0][1]
            x.depth = data[1][0]
            x.classId = data[2][0]
        #process data
        print(data)
   
if __name__ == "__main__":
    q = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=producer, args=(q, ))
    p2 = multiprocessing.Process(target=consumer, args=(q, ))
    
    p1.start()
    p2.start()
    
    
    #p1.join()
    #p2.join()

