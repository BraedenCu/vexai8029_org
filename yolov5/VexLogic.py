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
            ballsInGoals = []
            goalContentsArr = [] #2d array containing the ball contents of the goal arrays (indexed in the same way as goals arr)
            goalsToDescoreRed = []
            goalsToDescoreBlue = []
            goalsToScore = []
            detectInfoList = []
            
            #populate arrays
            for det in detections:
                #det.display()
                if det.classId == 0 or det.classId == 1: 
                    ballsArr.append(det)
                    
                elif det.classId == 2:
                    goalsArr.append(det)
            
            #iterate over goals to determine balls in goal and add those balls to goal datastructure   
            #logging.info(goalsArr)    
            if goalsArr:
                #logging.info("got here")
                for d in range(0, len(goalsArr)):
                    #logging.info("iterating over goals")
                    redBalls = 0
                    blueBalls = 0
                    ballsInGoal = []
                    #ownership = None
                    #logging.info(d)
                    goal = goalsArr[d]
                    gx = int(goal.left + (goal.right - goal.left)/2)
                    gy = int(goal.top + (goal.bottom - goal.top)/2)
                    gh, gw = goal.height, goal.width
                    #logging.info("addedGoalToDescore")
                    
                    for b in ballsArr:
                        bx = int(b.left + (b.right - b.left)/2)
                        by = int(b.top + (b.bottom - b.top)/2)
                        if ((bx > (gx - 0.5*gw) and bx < (gx + 0.5*gw))) and ((by > (gy - gy) and by < (gy + gy))):
                        #UNTESTED v VERSION using updated goal detection 
                        #if (bx > (goal.left) and bx < (goal.right)) and ((by > goal.bottom) and by < goal.top):
                            ballsInGoal.append(b) #add to local list of balls in individual goal being iterated over
                            ballsInGoals.append(b) #add to total list of all balls in goals
                            if b.classId == 0:
                                redBalls+=1
                            elif b.classId == 1:
                                blueBalls+=1
                            #logging.info("ball in goal")
                            #REMOVE BALL FROM REGULAR BALL CALCULATION (dont want bot going after balls in goals)
                        else:
                            ballsNotInGoals.append(b)
                    
                    #logging.info(redBalls)
                    
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
                    #logging.info(ballsInGoal)
                    for i in ballsInGoal: 
                        if topBall==None or i.top > topBall.top:
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
            else:
                #no goals, so all balls are appended to ballsNotInGoals
                for b in ballsArr:
                    ballsNotInGoals.append(b)
            
            #if we are descoring, find closest ball for each color to descore
            descoring = True

            closestGoalToDescoreRed = None
            closestGoalToDescoreBlue = None
            
            #logging.info(len(goalsToDescoreRed))
            
            if descoring == True and goalsToDescoreRed: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                #logging.info("running")
                #logging.info(len(goalsToScore))
                for goal in goalsToDescoreRed:
                    if closestGoalToDescoreRed == None:
                        closestGoalToDescoreRed = goal
                    else:
                        if closestGoalToDescoreRed.distance > goal.distance:
                            closestGoalToDescoreRed = goal
                    
                #set detectInfo detection to closest goal to send to cortex
                if closestGoalToDescoreRed!=None:
                    self.detectInfo.confidence = closestGoalToDescoreRed.confidence
                    self.detectInfo.left       = closestGoalToDescoreRed.left
                    self.detectInfo.top        = closestGoalToDescoreRed.top
                    self.detectInfo.right      = closestGoalToDescoreRed.right
                    self.detectInfo.bottom     = closestGoalToDescoreRed.bottom
                    self.detectInfo.width      = closestGoalToDescoreRed.width
                    self.detectInfo.height     = closestGoalToDescoreRed.height
                    self.detectInfo.distance   = closestGoalToDescoreRed.distance
                    self.detectInfo.area       = closestGoalToDescoreRed.area
                    self.detectInfo.classId    = 50
                    #logging.info("added2")
                    detectInfoList.append(copy.copy(self.detectInfo))
            
            if descoring == True and goalsToDescoreBlue: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                #logging.info("running")
                #logging.info(len(goalsToScore))
                for goal in goalsToDescoreBlue:
                    if closestGoalToDescoreBlue == None:
                        closestGoalToDescoreBlue = goal
                    else:
                        if closestGoalToDescoreBlue.distance > goal.distance:
                            closestGoalToDescoreBlue = goal
                    
                #set detectInfo detection to closest goal to send to cortex
                if closestGoalToDescoreBlue!=None:
                    self.detectInfo.confidence = closestGoalToDescoreBlue.confidence
                    self.detectInfo.left       = closestGoalToDescoreBlue.left
                    self.detectInfo.top        = closestGoalToDescoreBlue.top
                    self.detectInfo.right      = closestGoalToDescoreBlue.right
                    self.detectInfo.bottom     = closestGoalToDescoreBlue.bottom
                    self.detectInfo.width      = closestGoalToDescoreBlue.width
                    self.detectInfo.height     = closestGoalToDescoreBlue.height
                    self.detectInfo.distance   = closestGoalToDescoreBlue.distance
                    self.detectInfo.area       = closestGoalToDescoreBlue.area
                    self.detectInfo.classId    = 60 # blue goal descore
                    #logging.info("added2")
                    detectInfoList.append(copy.copy(self.detectInfo))
            
            
            #logging.info(ballsNotInGoals)
            
            
            #if we are collecting balls
            collectBall = True
            closestBallRed = None
            closestBallBlue = None
            
            #ballsNotInGoals
            if ballsNotInGoals:
                #logging.info("balls not in goals")
                #find the closestBall ball
                for b in ballsNotInGoals: 
                    #closest RED ball
                    if b.classId == 0:
                        if closestBallRed == None and b.classId == 0:
                            closestBallRed = b
                        elif (b.distance < closestBallRed.distance) and (closestBallRed.classId == 0): # class id must be red b/c we are on red team to track it
                            closestBallRed = b
                    #closest BLUE ball
                    if b.classId == 1:
                        if closestBallBlue == None and b.classId == 1: # class id must be red b/c we are on red team to track it
                            closestBallBlue = b
                        elif (b.distance < closestBallBlue.distance) and (closestBallBlue.classId == 1):
                            closestBallBlue = b

            
            #add red balls
            if collectBall and closestBallRed: #if closest ball is not == none and we are supposed to be collecting balls
                #send ball to collect coordinate
                #logging.info("added red ball")
                self.detectInfo.confidence = closestBallRed.confidence
                self.detectInfo.left       = closestBallRed.left
                self.detectInfo.top        = closestBallRed.top
                self.detectInfo.right      = closestBallRed.right
                self.detectInfo.bottom     = closestBallRed.bottom
                self.detectInfo.width      = closestBallRed.width
                self.detectInfo.height     = closestBallRed.height
                self.detectInfo.distance   = closestBallRed.distance
                self.detectInfo.area       = closestBallRed.area
                self.detectInfo.classId    = 10 #collect red ball
                
                detectInfoList.append(copy.copy(self.detectInfo))
            
            #add blue balls
            if collectBall and closestBallBlue!=None: #if closest ball is not == none and we are supposed to be collecting balls
                #send ball to collect coordinate
                self.detectInfo.confidence = closestBallBlue.confidence
                self.detectInfo.left       = closestBallBlue.left
                self.detectInfo.top        = closestBallBlue.top
                self.detectInfo.right      = closestBallBlue.right
                self.detectInfo.bottom     = closestBallBlue.bottom
                self.detectInfo.width      = closestBallBlue.width
                self.detectInfo.height     = closestBallBlue.height
                self.detectInfo.distance   = closestBallBlue.distance
                self.detectInfo.area       = closestBallBlue.area
                self.detectInfo.classId    = 20 #collect blue ball
                #logging.info("added")
                detectInfoList.append(copy.copy(self.detectInfo))
                
                 
            #find the closest goal for each team and send it to the brain
            #if we have a ball in our robot and need to score
            scoringBall = True
            closestGoal = None
            
            if scoringBall == True and goalsToScore!=None: #goals to score need to be detected to score
                #find closest goal, and go towards it 
                #logging.info("running")
                #logging.info(len(goalsToScore))
                for goal in goalsToScore:
                    if closestGoal == None:
                        closestGoal = goal
                    else:
                        if closestGoal.distance > goal.distance:
                            closestGoal = goal
                    
                #set detectInfo detection to closest goal to send to cortex
                if closestGoal!=None:
                    self.detectInfo.confidence = closestGoal.confidence
                    self.detectInfo.left       = closestGoal.left
                    self.detectInfo.top        = closestGoal.top
                    self.detectInfo.right      = closestGoal.right
                    self.detectInfo.bottom     = closestGoal.bottom
                    self.detectInfo.width      = closestGoal.width
                    self.detectInfo.height     = closestGoal.height
                    self.detectInfo.distance   = closestGoal.distance
                    self.detectInfo.area       = closestGoal.area
                    self.detectInfo.classId    = 30 #score red ball / blue ball
                    #logging.info("added2")
                    detectInfoList.append(copy.copy(self.detectInfo))
                
                
            #find the closest ball IN a goal and add it to the detect info list
            closestBallInGoal = None
            if ballsInGoals:
                for b in ballsInGoals:
                    if closestBallInGoal==None:
                        closestBallInGoal = b
                    else:
                        if closestBallInGoal.distance > b.distance:
                            closestBallInGoal = b
                            
                if closestBallInGoal:
                    #set closest ball in goal value
                    self.detectInfo.confidence = closestBallInGoal.confidence
                    self.detectInfo.left       = closestBallInGoal.left
                    self.detectInfo.top        = closestBallInGoal.top
                    self.detectInfo.right      = closestBallInGoal.right
                    self.detectInfo.bottom     = closestBallInGoal.bottom
                    self.detectInfo.width      = closestBallInGoal.width
                    self.detectInfo.height     = closestBallInGoal.height
                    self.detectInfo.distance   = closestBallInGoal.distance
                    self.detectInfo.area       = closestBallInGoal.area
                    self.detectInfo.classId    = 11 #score red ball / blue ball
                    #logging.info("added2")
                    detectInfoList.append(copy.copy(self.detectInfo))
            
            
            #if detectInfo is not empty, add it to vexBrain object
            if self.detectInfo:
                self.detectInfoList = detectInfoList
            
            #display elements of detect info list
            #logging.info(len(detectInfoList))
            for detect in detectInfoList:
                detect.display()
        
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
                #logging.info("brain has no targets")
                self.brain.setNoTargets()
            else:
                #self.detectInfo.display()
                #self.detectInfo.displayBrief()
                self.brain.addDetectList(self.detectInfoList)

