import array
import logging
import serial
import struct
import threading
import time
import zlib
import VexConfig
import DetectInfo

format = VexConfig.getLoggingFormat()
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

SyncBytes = [0xAA, 0x55, 0xCC, 0x33]

threadLock = threading.Lock()

def acquireLock():
    logging.info("  Lock acquire")
    threadLock.acquire()
    logging.info("  Lock acquired")

def releaseLock():
    logging.info("  Lock release")
    threadLock.release()
    logging.info("  Lock released")


class ClassIdType:
    RED  = 0
    BLUE = 1
    GOAL = 2

#------------------------------------------------------------------------------
class FifoObjectBoxType:
    "This class contains the data equivalent to the VEX C++ fifo_object_box"
    "structure."
    "// This structure represents a visual detection of a VEX object from the"
    "// forward facing depth camera. These objects are in reference to the"
    "// video image frame."
    "struct fifo_object_box {"
    "  // The center position of this object where [0,0] is the upper left of"
    "  // the video frame. Resolution is 320*240."
    "  int32  x;       // X position, Max is 320"
    "  int32  y;       // Y position, Max is 240"
    "  int32  width;   // Width of boundin box of this object"
    "  int32  height;  // Height of boundin box of this object"
    "  int32  classID; // Class ID of this object. 0=RED, 1=BLUE, 2=GOAL"
    "  float  depth;   // Depth of this object in mm from the camera"
    "  float  prob;    // Probability that this object is the class, 1.0==100%"
    "};"

    def __init__(self, index):
        "Constructor for this object."
        self.mIndex    = index
        self.mIsActive = False
        self.x        = 0
        self.y        = 0
        self.width    = 0
        self.height   = 0
        self.classId  = 0
        self.depth    = 0.0
        self.prob     = 0.0

    def getPacked(self):
        "Return a packed structure that can be sent to the VEX Brain."
        # c: char
        # b: signed char
        # B: unsigned char
        # h: short
        # H: unsigned short
        # i: int
        # I: unsigned int
        # f: float
        s = struct.Struct('<iiiiiff')
        packedData = s.pack(self.x, self.y, self.width, self.height, self.classId, self.depth, self.prob)
        #logging.info("---FifoObjectBoxType---  DataLength=%d", s.size)
        #logging.info("%s", packedData.hex())
        return packedData

    def isActive(self):
        "Indicates whether this object is currently active."
        return self.mIsActive

    def printTerse(self):
        "Display the critical contents of the current object."
        if self.mIsActive == False:
            return
        logging.info("   FOBT%02d [%d,%d] %d*%d id=%d, d=%.1f, p=%.1f", self.mIndex, self.x, self.y, self.width, self.height, self.classId, self.depth, self.prob)

    def printVerbose(self):
        "Display all the contents of the current object."
        logging.info("---FifoObjectBox---")
        logging.info("   x          : %d", self.x)
        logging.info("   y          : %d", self.y)
        logging.info("   width      : %d", self.width)
        logging.info("   height     : %d", self.height)
        logging.info("   classId    : %d", self.classId)
        logging.info("   depth      : %.1f", self.depth)
        logging.info("   prob       : %.1f", self.prob)

    def reset(self):
        "Re-initialize the contents of this object."
        self.mIsActive = False
        self.x        = 0
        self.y        = 0
        self.width    = 0
        self.height   = 0
        self.classId  = 0
        self.depth    = 0.0
        self.prob     = 0.0

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        if self.mIndex == 0:
            self.mIsActive = True
            self.x        = 300
            self.y        = 301
            self.width    = 10
            self.height   = 10
            self.classId  = ClassIdType.RED
            self.depth    = 1.0
            self.prob     = 0.5
        elif self.mIndex == 1:
            self.mIsActive = True
            self.x        = 310
            self.y        = 311
            self.width    = 21
            self.height   = 21
            self.classId  = ClassIdType.BLUE
            self.depth    = 4.1
            self.prob     = 0.7

#------------------------------------------------------------------------------
class PosRecordType:
    "This class contains data equivalent to the VEX C++ POS_RECORD structure."
    "// This structure represents the robot's location in reference to the"
    "// center of the playing field."
    "struct POS_RECORD {"
    "  int32  framecnt;  // This counter increments each frame"
    "  int32  status;    // 0 = All good, != 0 : Not all good"
    "  // [x,y,z] coordinates in millimeters. [0,0] is middle of field."
    "  // Note: These coordinates are for the GPS Sensor (FLIR Camera)."
    "  // If you want to know the location fo the center of your robot,"
    "  // you will have to add an offset."
    "  float  x;         // X position"
    "  float  y;         // Y position"
    "  float  z;         // Z is mm from the field tiles"
    "  float  az;        // Azimuth of the robot in radians (Heading)"
    "  float  el;        // Elevation of the robot in radians (Pitch)"
    "  float  rot;       // Rotation/Tilt of the robot in radians (Roll)"
    "};"

    def __init__(self):
        "Constructor for this object."
        self.framecnt  = 0
        self.status    = 0
        self.x         = 0.0
        self.y         = 0.0
        self.z         = 0.0
        self.az        = 0.0
        self.el        = 0.0
        self.rot       = 0.0

    def getPacked(self):
        "Return a packed structure that can be sent to the VEX Brain."
        # c: char
        # b: signed char
        # B: unsigned char
        # h: short
        # H: unsigned short
        # i: int
        # I: unsigned int
        # f: float
        s = struct.Struct('<iiffffff')
        packedData = s.pack(self.framecnt, self.status, self.x, self.y, self.z, self.az, self.el, self.rot)
        #logging.info("---PosRecordType---  DataLength=%d", s.size)
        #logging.info(packedData.hex())
        return packedData

    def printTerse(self):
        "Display the critical contents of the current object."
        logging.info("   PR [%.1f,%.1f,%.1f] az=%.1f, el=%.1f rot=%.1f, fc=%d, s=%d", self.x, self.y, self.z, self.az, self.el, self.rot, self.framecnt, self.status)

    def printVerbose(self):
        "Display all the contents of the current object."
        logging.info("---PosRecord---")
        logging.info("   framecnt   : %d", self.framecnt)
        logging.info("   status     : %d", self.status)
        logging.info("   x          : %.1f", self.x)
        logging.info("   y          : %.1f", self.y)
        logging.info("   z          : %.1f", self.z)
        logging.info("   az         : %.1f", self.az)
        logging.info("   el         : %.1f", self.el)
        logging.info("   rot        : %.1f", self.rot)

    def reset(self):
        "Re-initialize the contents of this object."
        self.framecnt  = 0
        self.status    = 0
        self.x         = 0.0
        self.y         = 0.0
        self.z         = 0.0
        self.az        = 0.0
        self.el        = 0.0
        self.rot       = 0.0

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        self.framecnt  = 9
        self.status    = 0
        self.x         = 0.1
        self.y         = 0.2
        self.z         = 0.3
        self.az        = 0.4
        self.el        = 0.5
        self.rot       = 0.6

#------------------------------------------------------------------------------
class MapObjectsType:
    "This class contains data equivalent to the VEX C++ MAP_OBJECTS"
    "structure."
    "// This structure represents a visual detection of a VEX object from the"
    "// forward facing depth camera. These objects are in reference to the"
    "// playing field."
    "struct MAP_OBJECTS {"
    "  int32   age;        // Number of iterations snice last valid measurement"
    "  int32   classID;    // Class ID of the object 0=RED, 1=BLUE"
    "  // Position field coordinates in millimeters."
    "  // Position [0,0] is in the middle of the field."
    "  float   positionX;  // X position"
    "  float   positionY;  // Y position"
    "  float   positionZ;  // Z represents height above the field tiles."
    "};"

    def __init__(self, index):
        "Constructor for this object."
        self.mIndex     = index
        self.mIsActive = False
        self.age       = 0
        self.classId   = 0
        self.positionX = 0.0
        self.positionY = 0.0
        self.positionZ = 0.0

    def getPacked(self):
        "Return a packed structure that can be sent to the VEX Brain."
        # c: char
        # b: signed char
        # B: unsigned char
        # h: short
        # H: unsigned short
        # i: int
        # I: unsigned int
        # f: float
        s = struct.Struct('<iifff')
        packedData = s.pack(self.age, self.classId, self.positionX, self.positionY, self.positionZ)
        #logging.info("---MapObjectsType---  DataLength=%d", s.size)
        #logging.info(packedData.hex())
        return packedData

    def isActive(self):
        "Indicates whether this object is currently active."
        return self.mIsActive

    def printTerse(self):
        "Display the critical contents of the current object."
        if self.mIsActive == False:
            return
        logging.info("   MO%02d [%.1f,%.1f,%.1f] id=%d, age=%d", self.mIndex, self.positionX, self.positionY, self.positionZ, self.classId, self.age)

    def printVerbose(self):
        "Display all the contents of the current object."
        logging.info("---MapObjects---")
        logging.info("   age        : %d", self.age)
        logging.info("   classId    : %d", self.classId)
        logging.info("   positionX  : %.1f", self.positionX)
        logging.info("   positionY  : %.1f", self.positionY)
        logging.info("   positionZ  : %.1f", self.positionZ)

    def reset(self):
        "Re-initialize the contents of this object."
        self.mIsActive = False
        self.age        = 0
        self.classId    = 0
        self.positionX  = 0.0
        self.positionY  = 0.0
        self.positionZ  = 0.0

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        if self.mIndex == 0:
            self.mIsActive = True
            self.age        = 20
            self.classId    = ClassIdType.GOAL
            self.positionX  = 3.1
            self.positionY  = 2.2
            self.positionZ  = 1.3

#------------------------------------------------------------------------------
class MapRecordType:
    "This class contains data equivalent the the VEX C++ MAP_RECORD structure."
    "// The MAP_RECORD contains everything"
    "struct MAP_RECORD {"
    "  int32       boxnum;  // Number of objects in the boxobj array"
    "  int32       mapnum;  // Number of objects in the mapobj array"
    "  POS_RECORD  pos;     // Position record for the robot's position"
    "  fifo_object_box  boxobj[MAX_OBJECT];  // Detected image objects"
    "  MAP_OBJECTS      maxobj[MAX_OBJECT];  // Detected map objects"
    "};"

    MAX_NUM_OBJECTS = 50

    def __init__(self):
        "Constructor for this object."
        self.boxnum        = 0
        self.mapnum        = 0
        self.posRecord     = PosRecordType()
        self.fifoObjBoxes  = []
        self.mapObjs       = []
        for cnt in range(0, self.MAX_NUM_OBJECTS):
            fobt = FifoObjectBoxType(cnt)
            self.fifoObjBoxes.append(fobt)
        for cnt in range(0, self.MAX_NUM_OBJECTS):
            mo = MapObjectsType(cnt)
            self.mapObjs.append(mo)

    def getNumBoxes(self):
        "Return the number of active box objects."
        numBoxes = 0
        for fobt in self.fifoObjBoxes:
            if fobt.isActive():
                numBoxes += 1
        return numBoxes

    def getNumMaps(self):
        "Return the number of active map objects."
        numMaps = 0
        for mo in self.mapObjs:
            if mo.isActive():
                numMaps += 1
        return numMaps

    def getPacked(self):
        "Return a packed structure that can be sent to the VEX Brain."
        # c: char
        # b: signed char
        # B: unsigned char
        # h: short
        # H: unsigned short
        # i: int
        # I: unsigned int
        # f: float
        s = struct.Struct('<ii')
        packedData = s.pack(self.boxnum, self.mapnum)
        packedData += self.posRecord.getPacked()
        for fobt in self.fifoObjBoxes:
            if fobt.isActive():
                packedData += fobt.getPacked()
        for mo in self.mapObjs:
            if mo.isActive():
                packedData += mo.getPacked()
        #logging.info("---MapRecordType---  DataLength=%d", s.size)
        #logging.info(packedData.hex())
        return packedData

    def printTerse(self):
        "Display the critical contents of the current object."
        logging.info("   MR numBoxes=%d, numMaps=%d", self.boxnum, self.mapnum)
        self.posRecord.printTerse()
        for fobt in self.fifoObjBoxes:
            fobt.printTerse()
        for mo in self.mapObjs:
            mo.printTerse()

    def printVerbose(self):
        "Display all the contents of the current object."
        logging.info("---MapRecord---")
        logging.info("   boxnum     : %d", self.boxnum)
        logging.info("   mapnum     : %d", self.mapnum)
        self.posRecord.printVerbose()
        for fobt in self.fifoObjBoxes:
            fobt.printVerbose()
        for mo in self.mapObjs:
            mo.printVerbose()

    def reset(self):
        "Re-initialize the contents of this object."
        self.boxnum     = 0
        self.mapnum     = 0
        self.posRecord.reset()
        for fobt in self.fifoObjBoxes:
            fobt.reset()
        for mo in self.mapObjs:
            mo.reset()

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        self.boxnum     = 2
        self.mapnum     = 1
        self.posRecord.setTestData()
        for fobt in self.fifoObjBoxes:
            fobt.setTestData()
        for mo in self.mapObjs:
            mo.setTestData()

#------------------------------------------------------------------------------
class MapPacketType:
    "This class contains data equivalent to the VEX C++ map_packet structure."
    "// Packet from Jetson to Brain"
    "struct __attribute__((__packed__)) map_packet {"
    "  // 12 Byte header"
    "  uint8  sync[4];  // 4 unique bytes that act as sync"
    "  uint16 length;   // Length of MAP_RECORD payload, doesn't include header"
    "  uint16 type;     // Type of packet"
    "  uint32 crc32;    // CRC32 of payload"
    "  // Payload"
    "  MAP_RECORD map;  // Map data"
    "};"

    def __init__(self):
        "Constructor for this object."
        self.sync = SyncBytes
        self.length  = 0
        self.type    = 1   # MAP_PACKET_TYPE from VEX Code
        self.crc32   = 0
        self.map     = MapRecordType()

    def getPackedMsg(self):
        "Return a packed structure that can be sent to the VEX Brain."
        # c: char
        # b: signed char
        # B: unsigned char
        # h: short
        # H: unsigned short
        # i: int
        # I: unsigned int
        # f: float
        packedData = self.map.getPacked()
        b = bytearray(packedData)
        #logging.info("..........")
        #logging.info(b.hex())
        #logging.info("..........")
        self.length = len(b)
        #self.crc32 = zlib.crc32(packedData)
        self.crc32 = zlib.crc32(b)
        s = struct.Struct('<BBBBHHI')
        packedHdr = s.pack(self.sync[0], self.sync[1], self.sync[2], self.sync[3], self.length, self.type, self.crc32)
        packedMsg = packedHdr + packedData
        #logging.info("---MapPacketType---  HdrLength=%d", s.size)
        #logging.info("  Length=%04X, CalcCRC32=%08X", self.length, self.crc32)
        #logging.info(packedMsg.hex())
        return packedMsg

    def printTerse(self):
        "Display the critical contents of the current object."
        logging.info("   MP %02X%02X%02X%02X %d %08x", self.sync[0], self.sync[1], self.sync[2], self.sync[3], self.length, self.crc32)
        self.map.printTerse()

    def printVerbose(self):
        "Display all the contents of the current object."
        logging.info("---MapPacket---")
        logging.info("   sync       : %02X %02X %02X %02X", self.sync[0], self.sync[1], self.sync[2], self.sync[3])
        logging.info("   length     : %d", self.length)
        logging.info("   crc32      : %08X", self.crc32)
        self.map.printVerbose()

    def reset(self):
        "Re-initialize the contents of this object."
        self.sync = SyncBytes
        self.length  = 0
        self.crc32   = 0
        self.map.reset()

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        self.map.setTestData()

#------------------------------------------------------------------------------
class VexBrain:
    __instance = None

    def __init__(self):
        "Constructor for this object."
        if VexBrain.__instance != None:
            raise Exception("VexBrain - Singleton error in __init__")
        else:
            VexBrain.__instance = self
            self.detectInfo = None
            self.msgRxCnt = 0
            self.msgTxCnt = 0
            self.brain = None
            self.mpt = None
            self.numTargets = 0
            try:
                self.brain = serial.Serial("/dev/ttyACM1", 115200, timeout=1)
                self.mpt = MapPacketType()
            except:
                logging.info("***ERROR***; Couldn't open /dev/ttyACM1")

    def addDetect(self, detectInfo):
        "Add detection info of an object from VexLogic."
        if self.numTargets == 0:
            #logging.info("Setting numTargets to 1")
            self.numTargets = 1
        if self.detectInfo == None:
            self.detectInfo = detectInfo
            #self.detectInfo.display()

    def addMap(self):
        "TBD"
        # TBD - Finish

    def clearMsg(self):
        "TBD"
        self.mpt.reset()

    def createMsgFromDetectInfo(self):
        "Build a message to send to the VEX Cortex Brain, based on detect info."
        #logging.info("createMsgFromDetectInfo - Enter")
        self.clearMsg()
        #self.setTestData2()
        #self.setTestData3()
        #self.setTestData4()
        numBoxes = self.numTargets   # TBD - Use actual number
        numMaps  = 0   # TBD - Use actual number
        self.mpt.map.boxnum                    = numBoxes
        self.mpt.map.mapnum                    = numMaps
        self.mpt.map.posRecord.framecnt        = self.msgTxCnt
        self.mpt.map.posRecord.status          = 0  # TBD - Finish
        self.mpt.map.posRecord.x               = 0.1  # TBD - Finish
        self.mpt.map.posRecord.y               = 0.2  # TBD - Finish
        self.mpt.map.posRecord.z               = 0.3  # TBD - Finish
        self.mpt.map.posRecord.az              = 0.4  # TBD - Finish
        self.mpt.map.posRecord.el              = 0.5  # TBD - Finish
        self.mpt.map.posRecord.rot             = 0.6  # TBD - Finish
        for cnt in range(0, numBoxes):
            self.mpt.map.fifoObjBoxes[cnt].mIsActive = True
            self.mpt.map.fifoObjBoxes[cnt].x         = int(self.detectInfo.left)
            self.mpt.map.fifoObjBoxes[cnt].y         = int(self.detectInfo.top)
            self.mpt.map.fifoObjBoxes[cnt].width     = int(self.detectInfo.width)
            self.mpt.map.fifoObjBoxes[cnt].height    = int(self.detectInfo.height)
            self.mpt.map.fifoObjBoxes[cnt].classId   = ClassIdType.RED    # TBD
            self.mpt.map.fifoObjBoxes[cnt].depth     = int(self.detectInfo.distance)
            self.mpt.map.fifoObjBoxes[cnt].prob      = self.detectInfo.confidence
        for cnt in range(0, numMaps):
            self.mpt.map.mapObjs[cnt].mIsActive      = True
            self.mpt.map.mapObjs[cnt].age            = 20     # TBD
            self.mpt.map.mapObjs[cnt].classId        = ClassIdType.GOAL    # TBD
            self.mpt.map.mapObjs[cnt].positionX      = 3.1    # TBD
            self.mpt.map.mapObjs[cnt].positionY      = 2.2    # TBD
            self.mpt.map.mapObjs[cnt].positionZ      = 1.3    # TBD
        #logging.info("createMsgFromDetectInfo - Exit")

    def getInstance():
        "Static access method to get the Singleton instance."
        logging.info("VexBrain.getInstance()")
        if VexBrain.__instance == None:
            VexBrain()
        return VexBrain.__instance

    def setNoTargets(self):
        "Indicate there were no targets detected in the last go around."
        if self.numTargets != 0:
            #logging.info("Setting numTargets to 0")
            self.numTargets = 0

    def setTestData(self):
        "Set up test data, for debugging protocol with Brain."
        #logging.info("setTestData - Enter")
        self.mpt.setTestData()
        #logging.info("setTestData - Exit")

    def setTestData2(self):
        "Set up test data, for debugging protocol with Brain."
        #logging.info("setTestData2 - Enter")
        self.mpt.map.boxnum                    = 2
        self.mpt.map.mapnum                    = 1
        self.mpt.map.posRecord.framecnt        = 9
        self.mpt.map.posRecord.status          = 0
        self.mpt.map.posRecord.x               = 0.1
        self.mpt.map.posRecord.y               = 0.2
        self.mpt.map.posRecord.z               = 0.3
        self.mpt.map.posRecord.az              = 0.4
        self.mpt.map.posRecord.el              = 0.5
        self.mpt.map.posRecord.rot             = 0.6
        self.mpt.map.fifoObjBoxes[0].mIsActive = True
        self.mpt.map.fifoObjBoxes[0].x         = 300
        self.mpt.map.fifoObjBoxes[0].y         = 301
        self.mpt.map.fifoObjBoxes[0].width     = 10
        self.mpt.map.fifoObjBoxes[0].height    = 10
        self.mpt.map.fifoObjBoxes[0].classId   = ClassIdType.RED
        self.mpt.map.fifoObjBoxes[0].depth     = 1.0
        self.mpt.map.fifoObjBoxes[0].prob      = 0.5
        self.mpt.map.fifoObjBoxes[1].mIsActive = True
        self.mpt.map.fifoObjBoxes[1].x         = 310
        self.mpt.map.fifoObjBoxes[1].y         = 311
        self.mpt.map.fifoObjBoxes[1].width     = 21
        self.mpt.map.fifoObjBoxes[1].height    = 21
        self.mpt.map.fifoObjBoxes[1].classId   = ClassIdType.BLUE
        self.mpt.map.fifoObjBoxes[1].depth     = 4.1
        self.mpt.map.fifoObjBoxes[1].prob      = 0.7
        self.mpt.map.mapObjs[0].mIsActive      = True
        self.mpt.map.mapObjs[0].age            = 20
        self.mpt.map.mapObjs[0].classId        = ClassIdType.GOAL
        self.mpt.map.mapObjs[0].positionX      = 3.1
        self.mpt.map.mapObjs[0].positionY      = 2.2
        self.mpt.map.mapObjs[0].positionZ      = 1.3
        #logging.info("setTestData2 - Exit")

    def setTestData3(self):
        "Set up test data, for debugging protocol with Brain."
        #logging.info("setTestData3 - Enter")
        self.mpt.map.boxnum                    = 1
        self.mpt.map.mapnum                    = 1
        self.mpt.map.posRecord.framecnt        = 9
        self.mpt.map.posRecord.status          = 0
        self.mpt.map.posRecord.x               = 0.1
        self.mpt.map.posRecord.y               = 0.2
        self.mpt.map.posRecord.z               = 0.3
        self.mpt.map.posRecord.az              = 0.4
        self.mpt.map.posRecord.el              = 0.5
        self.mpt.map.posRecord.rot             = 0.6
        self.mpt.map.fifoObjBoxes[0].mIsActive = True
        self.mpt.map.fifoObjBoxes[0].x         = 300
        self.mpt.map.fifoObjBoxes[0].y         = 301
        self.mpt.map.fifoObjBoxes[0].width     = 10
        self.mpt.map.fifoObjBoxes[0].height    = 10
        self.mpt.map.fifoObjBoxes[0].classId   = ClassIdType.RED
        self.mpt.map.fifoObjBoxes[0].depth     = 1.0
        self.mpt.map.fifoObjBoxes[0].prob      = 0.5
        self.mpt.map.mapObjs[0].mIsActive      = True
        self.mpt.map.mapObjs[0].age            = 20
        self.mpt.map.mapObjs[0].classId        = ClassIdType.GOAL
        self.mpt.map.mapObjs[0].positionX      = 3.1
        self.mpt.map.mapObjs[0].positionY      = 2.2
        self.mpt.map.mapObjs[0].positionZ      = 1.3
        #logging.info("setTestData3 - Exit")

    def setTestData4(self):
        "Set up test data, for debugging protocol with Brain."
        #logging.info("setTestData4 - Enter")
        self.mpt.map.boxnum                    = 1
        self.mpt.map.mapnum                    = 0
        self.mpt.map.posRecord.framecnt        = 9
        self.mpt.map.posRecord.status          = 0
        self.mpt.map.posRecord.x               = 0.1
        self.mpt.map.posRecord.y               = 0.2
        self.mpt.map.posRecord.z               = 0.3
        self.mpt.map.posRecord.az              = 0.4
        self.mpt.map.posRecord.el              = 0.5
        self.mpt.map.posRecord.rot             = 0.6
        self.mpt.map.fifoObjBoxes[0].mIsActive = True
        self.mpt.map.fifoObjBoxes[0].x         = 300
        self.mpt.map.fifoObjBoxes[0].y         = 301
        self.mpt.map.fifoObjBoxes[0].width     = 10
        self.mpt.map.fifoObjBoxes[0].height    = 10
        self.mpt.map.fifoObjBoxes[0].classId   = ClassIdType.RED
        self.mpt.map.fifoObjBoxes[0].depth     = 1.0
        self.mpt.map.fifoObjBoxes[0].prob      = 0.5
        #logging.info("setTestData4 - Exit")

    def startComm(self):
        "Start communicating with the VEX Cortex Brain."
        # VEX Brain request for data (it sends ASCII data currently):
        #     b'AA55CC3301\r\n'
        lastMsg = None

        logging.info("VexBrain - Entering processing infinite loop")
        while True:
            try:
                data = self.brain.readline()
                if data:
                    self.msgRxCnt += 1
                    #logging.info("RX : %04d %s", self.msgRxCnt, data)
                    #if (self.msgRxCnt % 10) == 0:
                    #if (self.msgRxCnt % 1) == 0:
                    if self.detectInfo != None:
                        self.createMsgFromDetectInfo()
                        self.detectInfo.displayBrief()
                        packedMsg = self.mpt.getPackedMsg()
                        #if lastMsg != packedMsg:
                        #    logging.info("TX : %s", packedMsg.hex())
                        self.brain.write(packedMsg)
                        self.msgTxCnt += 1
                        lastMsg = packedMsg
                        #break
            except:
                break

    def threadEntry(self):
        "Entry point for the VEX Brain Comm thread."
        threading.current_thread().name = "tBrain"
        logging.info("")
        logging.info("-----------------------")
        logging.info("--- Thread starting ---")
        logging.info("-----------------------")
        logging.info("")

        self.startComm()

        if self.brain != None:
            self.brain.close()

        logging.info("")
        logging.info("------------------------")
        logging.info("--- Thread finishing ---")
        logging.info("------------------------")
        logging.info("")

