import logging
import threading
import time
import VexConfig
import VexBrain
import DetectInfo
import DetectRealSense
import FlirPosInfo

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class VexLogic:
    "TBD"
    __instance = None

    def __init__(self):
        "Constructor for this object."
        if VexLogic.__instance != None:
            raise Exception("VexLogic - Singleton error in __init__")
        else:
            VexLogic.__instance = self
            self.brain = None
            self.detectInfo = None
            self.numTargets = 0
            self.lock = threading.Lock()

    def addDetectRealSense(self, detectRealSense):
        "Add detection info of an object from the RealSense camera."
        with self.lock:
            self.setDetectInfo(detectRealSense)
            #self.detectInfo.displayBrief()

    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexLogic.getInstance()")
        if VexLogic.__instance == None:
            VexLogic()
        return VexLogic.__instance

    def setDetectInfo(self, detectRealSense):
        "Set up the DetectInfo based on RealSense info."
        
        #detectRealSense.display()
        
        if self.numTargets == 0:
            logging.info("Setting numTargets to 1")
            self.numTargets = 1
            
        if self.detectInfo == None:
            self.detectInfo = DetectInfo.DetectInfo(detectRealSense.classId, detectRealSense.confidence)
        else:
            #prevents error that occours when bugged balls are detected with depth 0
            #print("runningthis")
            if detectRealSense.distance != 0:
                #if self.detectInfo.width == 0:
                #if detectRealSense.width != 0:
                #print("ran this")
                self.detectInfo.confidence = detectRealSense.confidence
                self.detectInfo.left       = detectRealSense.left
                self.detectInfo.top        = detectRealSense.top
                self.detectInfo.right      = detectRealSense.right
                self.detectInfo.bottom     = detectRealSense.bottom
                self.detectInfo.width      = detectRealSense.width
                self.detectInfo.height     = detectRealSense.height
                self.detectInfo.distance   = detectRealSense.distance
                self.detectInfo.area       = detectRealSense.area
                #print(self.detectInfo.distance)
                self.detectInfo.displayBrief()
                """
                else:
                    resultW = 0.0
                    resultH = 0.0
                    resultD = 0.0
                    if detectRealSense.width >= self.detectInfo.width:
                        increase = detectRealSense.width - self.detectInfo.width
                        resultW = increase / self.detectInfo.width
                    else:
                        increase = self.detectInfo.width - detectRealSense.width
                        resultW = increase / detectRealSense.width
                    if detectRealSense.height >= self.detectInfo.height:
                        increase = detectRealSense.height - self.detectInfo.height
                        resultH = increase / self.detectInfo.height
                    else:
                        increase = self.detectInfo.height - detectRealSense.height
                        resultH = increase / detectRealSense.height
                    if detectRealSense.distance >= self.detectInfo.distance:
                        increase = detectRealSense.distance - self.detectInfo.distance
                        resultD = increase / self.detectInfo.distance
                    else:
                        increase = self.detectInfo.distance - detectRealSense.distance
                        resultD = increase / detectRealSense.distance
                    if (resultW + resultH + resultD) < 0.7:
                        self.detectInfo.confidence = detectRealSense.confidence
                        self.detectInfo.left       = detectRealSense.left
                        self.detectInfo.top        = detectRealSense.top
                        self.detectInfo.right      = detectRealSense.right
                        self.detectInfo.bottom     = detectRealSense.bottom
                        self.detectInfo.width      = detectRealSense.width
                        self.detectInfo.height     = detectRealSense.height
                        self.detectInfo.distance   = detectRealSense.distance
                        self.detectInfo.area       = detectRealSense.area
                        self.detectInfo.displayBrief()
                    else:
                        logging.info("---IGNORING--- W:%4.1f, H:%4.1f, D:%4.1f", resultW, resultH, resultD)
                    """
        #self.detectInfo.displayBrief()
        
        
    def setInstances(self, vb, vf, vr):
        "TBD"
        logging.info("VexLogic.setInstances()")
        self.brain = vb

    def setNoTargets(self):
        "Indicate there were no detects/targets in latest scan."
        if self.numTargets != 0:
            logging.info("Setting numTargets to 0")
            self.numTargets = 0

    def threadEntry(self):
        "Entry point for the VEX Logic thread."
        threading.current_thread().name = "tLogic"
        logging.info("")
        logging.info("-----------------------")
        logging.info("--- Thread starting ---")
        logging.info("-----------------------")
        logging.info("")
        
        logging.info("VexLogic - Entering processing infinite loop")
        while True:
            time.sleep(0.07)
            self.updateBrain()

        logging.info("")
        logging.info("------------------------")
        logging.info("--- Thread finishing ---")
        logging.info("------------------------")
        logging.info("")

    def updateBrain(self):
        "Send the VEX Cortex Brain the latest object position info."
        # TBD - LockGet()
        with self.lock:
            if self.numTargets == 0 or self.detectInfo == None:
                #print("brain has no targets")
                logging.info("brain has no targets")
                self.brain.setNoTargets()
            else:
                #self.detectInfo.display()
                #self.detectInfo.displayBrief()
                self.brain.addDetect(self.detectInfo)

