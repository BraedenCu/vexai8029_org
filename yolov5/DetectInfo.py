import logging
import math
import VexConfig

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

#------------------------------------------------------------------------------
class DetectInfo:
    "TBD"

    def __init__(self, classId, confidence):
        "Constructor for this object."
        self.classId    = classId #0  = undefined
                                  #10 = closest generic red ball
                                  #11 = closest red ball OUTSIDE goal
                                  #12 = closest red ball IN goal
                                  #20 = closest generic blue ball
                                  #21 = closest blue ball OUTSIDE goal
                                  #22 = closest blue ball IN goal
                                  #30 = closest generic goal
                                  #31 = closest blue/red goal to score
                                  #32 = closest red goal to descore (closestGoalToDescoreRed)
                                  #33 = closest blue goal to descore (closestGoalToDescoreBlue)

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
        centerLr = self.left + (self.right - self.left)/2
        centerTb = self.top + (self.bottom - self.top)/2
        logging.info("Center:[%5.1f, %5.1f], Distance=TBD", centerLr, centerTb)
        logging.info("ID:%2d, L:%5.1f, T:%5.1f, R:%5.1f, B:%5.1f, W:%5.1f, H:%5.1f, D:%5.1f, A:%9.1f, C:%4.2f", self.classId, self.left, self.top, self.right, self.bottom, self.width, self.height, self.distance, self.area, self.confidence)

    def displayBrief(self):
        "Display brief contents of the current object."
        centerLr = self.left + (self.right - self.left)/2
        centerTb = self.top + (self.bottom - self.top)/2
        logging.info("[%4.0f,%4.0f] W:%4.0f, H:%4.0f, D:%4.0f, Conf=%4.2f", centerLr, centerTb, self.width, self.height, self.distance, self.confidence)

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

