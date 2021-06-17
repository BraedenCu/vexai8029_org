import logging
import VexConfig

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class DetectionRealsense:
    def __init__(self, classId, confidence):
        self.classId    = classId
        self.confidence = confidence
        self.left       = 0.0
        self.top        = 0.0
        self.right      = 0.0
        self.bottom     = 0.0
        self.width      = 0.0
        self.height     = 0.0
        self.area       = 0.0
        self.distance   = 0.0
    
    def display(self):
        "Display contents of the current object."
        logging.info("ID:%2d, L:%5.1f, T:%5.1f, R:%5.1f, B:%5.1f, W:%5.1f, H:%5.1f, D:%5.1f, A:%9.1f, C:%3.1f", self.classId, self.left, self.top, self.right, self.bottom, self.width, self.height, self.distance, self.area, self.confidence)

    def setBox(self, left, top, right, bottom, width, height, distance, area):
        "Constructor for this object."
        self.left      = left
        self.top       = top
        self.right     = right
        self.bottom    = bottom
        self.width     = width
        self.height    = height
        self.area      = area
        self.distance  = distance
    
class DetectRealSense:
    "TBD"

    def __init__(self):
        "Constructor for this object."
        self.ballArr = []
        self.goalArr = []

    def addBall(self, ball):
        self.ballArr.append(ball)
        logging.info("appended ball")
    
    def addGoal(self, goal):
        self.goalArr.append(goal)
        logging.info("appended goal")
    
    def displayClosestBall(self):
        if self.ballArr:
            closest = self.ballArr[0]
            for ball in self.ballArr:
                if ball.distance < closest.distance:
                    closest = ball
                    
            logging.info("ID:%2d, L:%5.1f, T:%5.1f, R:%5.1f, B:%5.1f, W:%5.1f, H:%5.1f, D:%5.1f, A:%9.1f, C:%3.1f", closest.classId, closest.left, closest.top, closest.right, closest.bottom, closest.width, closest.height, closest.distance, closest.area, closest.confidence)
        
        
        
    
    

