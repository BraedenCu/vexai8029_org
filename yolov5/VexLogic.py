import logging
import threading
import time
import VexConfig
import VexBrain
import DetectInfo
import DetectRealSense
import FlirPosInfo
import copy

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
            self.detectInfoList = None
            self.ballArr = None
            self.goalArr = None
            self.numTargets = 0
            self.lock = threading.Lock()


    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexLogic.getInstance()")
        if VexLogic.__instance == None:
            VexLogic()
        return VexLogic.__instance


    def determineClosest(self, arr, outputId):
        closest = None
        #0.7 = confidence, just a random value 
        detectInfo = DetectInfo.DetectInfo(outputId, 0.7)
        if arr:
            for b in arr:
                if closest == None:
                    closest = b
                else:
                    if closest.distance > b.distance:
                        closest = b
            
            if closest!=None:
                detectInfo.confidence = closest.confidence
                detectInfo.left       = closest.left
                detectInfo.top        = closest.top
                detectInfo.right      = closest.right
                detectInfo.bottom     = closest.bottom
                detectInfo.width      = closest.width
                detectInfo.height     = closest.height
                detectInfo.distance   = closest.distance
                detectInfo.area       = closest.area
                detectInfo.classId    = outputId
                            
        #create detect info object and return detect info object
        return detectInfo
            
            
            
        

    def setDetectInfoArray(self, detections):
        if self.numTargets == 0:
            logging.info("Setting numTargets to 1")
            self.numTargets = 1
        
        #dont really understand this or the above code
        if self.detectInfo == None:
            self.detectInfo = DetectInfo.DetectInfo(detections[0].classId, detections[0].confidence)
        else:    
            goalsArr = [] #Goals
            ballsArr = [] #all balls
            blueBallsArr = []
            redBallsArr = []
            redBallsNotInGoals = [] #balls not in goals
            blueBallsNotInGoals = [] #balls not in goals
            redBallsInGoals = [] 
            blueBallsInGoals = []
            goalContentsArr = [] #2d array containing the ball contents of the goal arrays (indexed in the same way as goals arr)
            goalsToDescoreRed = []
            goalsToDescoreBlue = []
            goalsToScore = []
            detectInfoList = [] # list of all detections to be sent to brain
            
            #populate arrays
            for det in detections:
                
                if det.classId == 0: 
                    ballsArr.append(det)
                    redBallsArr.append(det)
                elif det.classId == 1:
                    ballsArr.append(det)
                    blueBallsArr.append(det)
                elif det.classId == 2:
                    goalsArr.append(det)
            
            #iterate over goals to determine balls in goal and add those balls to goal datastructure   
            if goalsArr:
                for d in range(0, len(goalsArr)):
                    redBalls = 0 # total red balls in goal
                    blueBalls = 0 # total blue balls in goal
                    ballsInGoal = []

                    goal = goalsArr[d]
                    gx = int(goal.left + (goal.right - goal.left)/2)
                    gy = int(goal.top + (goal.bottom - goal.top)/2)
                    gh, gw = goal.height, goal.width
                    
                    for b in ballsArr:
                        bx = int(b.left + (b.right - b.left)/2)
                        by = int(b.top + (b.bottom - b.top)/2)
                        
                        if ((bx > (gx - 0.5*gw) and bx < (gx + 0.5*gw))) and ((by > (gy - gy) and by < (gy + gy))):
                        #UNTESTED v VERSION using updated goal detection 
                        #if (bx > (goal.left) and bx < (goal.right)) and ((by > goal.bottom) and by < goal.top):
                            #BALL IS IN GOAL
                            ballsInGoal.append(b) #add to local list of balls in individual goal being iterated over

                            if b.classId == 0:
                                redBallsInGoals.append(b) #add to total list of all red balls in goals
                                #redBallsArr.append(b)
                                redBalls+=1
                                
                            elif b.classId == 1:
                                blueBallsInGoals.append(b) #add to total list of all blue balls in goals
                                #blueBallsArr.append(b)
                                blueBalls+=1 
                        
                        else:
                            #BALL IS NOT IN GOAL, DO NOT ADD TO GOAL TOTALS
                            if b.classId == 0:
                                redBallsNotInGoals.append(b) #add to total list of all red balls NOT in goals
                                redBallsArr.append(b)
                                
                            elif b.classId == 1:
                                blueBallsNotInGoals.append(b) #add to total list of all blue balls NOT in goals  
                                blueBallsArr.append(b)                  
                    
                    #if more blue than red, descore it if on red team
                    if blueBalls > redBalls:
                        goalsToDescoreRed.append(goal)
                    
                    #blue team goals to descore (if more red balls, descore if on blue team)
                    if redBalls > blueBalls:
                        #logging.info("added goal")
                        goalsToDescoreBlue.append(goal)
                        
                    #if total number of balls in goal is < 3, add it to goals to score array
                    #team does not matter because it is simply checking if the number of balls in the goal is > 3
                    if blueBalls + redBalls < 3:
                        goalsToScore.append(goal)
                    
                    #iterate over balls in goals
                    topBall = None
                    middleBall = None
                    bottomBall = None

                    for i in ballsInGoal: 
                        if topBall==None or i.top > topBall.top:
                            topBall = i
                        elif middleBall==None or i.top > middleBall.top:
                            middleBall = i
                        elif bottomBall==None or i.top > bottomBall.top:
                            bottomBall = i
                    
                    goalContentsArr.append([topBall, middleBall, bottomBall])
                    
            
            else:
                #no goals, so all balls are appended to ballsNotInGoals
                for b in ballsArr:
                    #BALL IS NOT IN GOAL, DO NOT ADD TO GOAL TOTALS
                    if b.classId == 0:
                        redBallsNotInGoals.append(b) #add to total list of all red balls NOT in goals
                        
                    elif b.classId == 1:
                        blueBallsNotInGoals.append(b) #add to total list of all blue balls NOT in goals      
            
            
            #if we are descoring, find closest ball for each color to descore
            descoring = False
                        
            if descoring and goalsToDescoreRed: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                detectinfo = self.determineClosest(goalsToDescoreRed, 32)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()
                
                
            if descoring and goalsToDescoreBlue: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                detectinfo = self.determineClosest(goalsToDescoreBlue, 33)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()

            #if we are collecting balls
            collectBall = True
            
            if collectBall and redBallsNotInGoals:
                #find the closest red ball not in goal
                detectinfo = self.determineClosest(redBallsNotInGoals, 11)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()
            
            if collectBall and blueBallsNotInGoals:
                #find the closest blue ball not in goal
                detectinfo = self.determineClosest(blueBallsNotInGoals, 21)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()
            
                   
            #find the closest goal for each team and send it to the brain
            #if we have a ball in our robot and need to score
            scoringBall = False
            closestGoal = None
            
            if scoringBall and goalsToScore: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                #logging.info("running")
                #logging.info(len(goalsToScore))
                detectinfo = self.determineClosest(goalsToScore, 31)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()
                
        
            #find the closest ball IN a goal and add it to the detect info list
            findclosestballingoal = True
            
            if findclosestballingoal:
                #find closest ball in goal
                if blueBallsInGoals:
                    detectinfo = self.determineClosest(blueBallsInGoals, 22)
                    detectInfoList.append(copy.copy(detectinfo))
                    #detectinfo.display()
                if redBallsInGoals:
                    detectinfo = self.determineClosest(redBallsInGoals, 12)
                    detectInfoList.append(copy.copy(detectinfo))
                    #detectinfo.display()
            
            #find the closest generic ball
            findclosestgenericball = True
            
            #logging.info(blueBalls)
            if findclosestgenericball:
                #find closest ball in goal
                if blueBallsArr:
                    detectinfo = self.determineClosest(blueBallsArr, 20)
                    detectInfoList.append(copy.copy(detectinfo))
                    #detectinfo.display()
                if redBallsArr:
                    detectinfo = self.determineClosest(redBallsArr, 10)
                    detectInfoList.append(copy.copy(detectinfo))
                    #detectinfo.display()
            
            #find the closest generic goal
            if goalsArr:
                detectinfo = self.determineClosest(goalsArr, 30)
                detectInfoList.append(copy.copy(detectinfo))
                #detectinfo.display()
                       
            #if detectInfo is not empty, add it to vexBrain object
            if self.detectInfo:
                self.detectInfoList = detectInfoList
            
            #display elements of detect info list
            #for detect in self.detectInfoList:
                #detect.display()
        
        
        

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
            if self.numTargets == 0 or self.detectInfoList == None:
                #print("brain has no targets")
                logging.info("brain has no targets")
                self.brain.setNoTargets()
            else:
                #self.detectInfoList[0].display()
                #self.detectInfo.displayBrief()
                self.brain.addDetectList(self.detectInfoList)

