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
            self.ballArr = None
            self.goalArr = None
            self.numTargets = 0
            self.lock = threading.Lock()

    def addDetectRealSense(self, ballArr, goalArr):
        "Add detection info of an object from the RealSense camera."
        with self.lock:
            self.setDetectInfo(ballArr, goalArr)
            #self.detectInfo.displayBrief()
    
    
    def addArrays(self, ballArr, goalArr):
        "Add detection info of a goal from the RealSense camera."
        with self.lock:
            self.goalArr = goalArr
            self.ballArr = ballArr
            self.setDetectInfoArr(self.goalArr, self.ballArr)

    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexLogic.getInstance()")
        if VexLogic.__instance == None:
            VexLogic()
        return VexLogic.__instance

    def setDetectInfoArray(self, detections):
        
        if self.numTargets == 0:
            logging.info("Setting numTargets to 1")
            self.numTargets = 1
            
        if self.detectInfo == None:
            self.detectInfo = DetectInfo.DetectInfo(detections[0].classId, detections[0].confidence)
        
        else:    
            goalsArr = [] #Goals
            ballsArr = [] #all balls
            ballsNotInGoals = [] #balls not in goals
            goalContentsArr = [] #2d array containing the ball contents of the goal arrays (indexed in the same way as goals arr)
            goalsToDescore = []
            
            #populate arrays
            for det in detections:
                #det.display()
                if det.classId == 0 or det.classId == 1: 
                    ballsArr.append(det)
                    
                elif det.classId == 2:
                    goalsArr.append(det)
            
            #iterate over goals to determine balls in goal and add those balls to goal datastructure       
            if goalsArr:
                for d in range(0, len(goalsArr)-1):
                    redBalls = 0
                    blueBalls = 0
                    ballsInGoal = []
                    ownership = None
                    gx = int(goalsArr[d].left + (goalsArr[d].right - goalsArr[d].left)/2)
                    gy = int(goalsArr[d].top + (goalsArr[d].bottom - goalsArr[d].top)/2)
                    gh, gw = goalsArr[d].height, goalsArr[d].width
                    for b in ballsArr:
                        bx = int(b.left + (b.right - b.left)/2)
                        by = int(b.top + (b.bottom - b.top)/2)
                        if bx > gx - 0.5*gw and bx < gx + 0.5*gw:
                            ballsInGoal.append(b)
                            #TBD: add y calculation, here is just checks if x is within the goal range
                            if b.classId == 0:
                                redBalls+=1
                            elif b.classId == 1:
                                blueBalls+=1
                            #logging.info("ball in goal")
                            #REMOVE BALL FROM REGULAR BALL CALCULATION (dont want bot going after balls in goals)
                        else:
                            ballsNotInGoals.append(b)
                    
                    #if more blue than red, descore it
                    if blueBalls > redBalls:
                        goalsToDescore.append(goalsArr[d])
                    
                    #iterate over balls in goals
                    topBall = None
                    middleBall = None
                    bottomBall = None
                    for i in ballsInGoal: 
                        if i==None or i.top > topBall.top:
                            topBall = i
                        elif middleBall==None or i.top > middleBall.top:
                            middleBall = i
                        elif bottomBall==None or i.top > bottomBall.top:
                            bottomBall = i
                    
                    goalContentsArr.append([topBall, middleBall, bottomBall])
                    
                    #check if we should descore this goal, and if so, append it to the to descore array in the format [0, 1, 0]
                    #1 means take ball out of goal, 0 means it is your teams color so leave it in. [-1, 0, 1] -1 means no ball is there
                    #for ball in goalContentsArr[d]: 
                    #    if ball.classId == 0: #assuming we are on red
                    #        goalsToDescore
            
            #if we are descoring, send the goal detection to the brain (there also must be a goal to descore in view)
            descoring = False
            if goalsToDescore:
                if descoring:
                    #for now just descore the first goal found that needs to be descored
                    self.detectInfo.confidence = goalsToDescore[0].confidence
                    self.detectInfo.left       = goalsToDescore[0].left
                    self.detectInfo.top        = goalsToDescore[0].top
                    self.detectInfo.right      = goalsToDescore[0].right
                    self.detectInfo.bottom     = goalsToDescore[0].bottom
                    self.detectInfo.width      = goalsToDescore[0].width
                    self.detectInfo.height     = goalsToDescore[0].height
                    self.detectInfo.distance   = goalsToDescore[0].distance
                    self.detectInfo.area       = goalsToDescore[0].area
            
            #if we are collecting balls
            collectBall = True
            closestBall = None
            
            #balls not in goals will only be populated if goals exist, otherwise just use balls
            if ballsNotInGoals:
                #find the closestBall ball
                for b in ballsNotInGoals:
                    if closestBall == None or b.distance < closestBall.distance and closestBall.classId == 0: # class id must be red b/c we are on red team to track it
                        closestBall = b
            else:
                for b in ballsArr:
                    #logging.info("running")
                    if closestBall == None or b.distance < closestBall.distance and closestBall.classId == 0: # class id must be red b/c we are on red team to track it
                    #logging.info("set this value")
                        closestBall = b
            
            #closestBall.display()
            #logging.info(closestBall.confidence)
            if collectBall and closestBall!=None: #if closest ball is not == none and we are supposed to be collecting balls
                #send ball to collect coordinate
                self.detectInfo.confidence = closestBall.confidence
                self.detectInfo.left       = closestBall.left
                self.detectInfo.top        = closestBall.top
                self.detectInfo.right      = closestBall.right
                self.detectInfo.bottom     = closestBall.bottom
                self.detectInfo.width      = closestBall.width
                self.detectInfo.height     = closestBall.height
                self.detectInfo.distance   = closestBall.distance
                self.detectInfo.area       = closestBall.area
                
            
            #display detectinfo
            if self.detectInfo:
                self.detectInfo.display()
            
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
            if detectRealSense.distance != 0:
                #if self.detectInfo.width == 0:
                #if detectRealSense.width != 0:
                if detectRealSense.distance > self.detectInfo.distance and self.detectInfo.distance != 0:
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
                #logging.info("brain has no targets")
                self.brain.setNoTargets()
            else:
                #self.detectInfo.display()
                #self.detectInfo.displayBrief()
                self.brain.addDetect(self.detectInfo)

