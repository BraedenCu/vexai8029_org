import array
import serial
import struct
import time
import zlib

SyncBytes = [0xAA, 0x55, 0xCC, 0x33]

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
        #print("---FifoObjectBoxType---  DataLength={0:d}".format(s.size))
        #print(packedData.hex())
        return packedData

    def isActive(self):
        "Indicates whether this object is currently active."
        return self.mIsActive

    def printTerse(self):
        "Display the critical contents of the current object."
        if self.mIsActive == False:
            return
        print("   FOBT{0:02d} [{1:d},{2:d}] {3:d}*{4:d} id={5:d}, d={6:.1f}, p={7:.1f}".format(self.mIndex, self.x, self.y, self.width, self.height, self.classId, self.depth, self.prob))

    def printVerbose(self):
        "Display all the contents of the current object."
        print("---FifoObjectBox---")
        print("   x          :", self.x)
        print("   y          :", self.y)
        print("   width      :", self.width)
        print("   height     :", self.height)
        print("   classId    :", self.classId)
        print("   depth      :", self.depth)
        print("   prob       :", self.prob)

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
        #print("---PosRecordType---  DataLength={0:d}".format(s.size))
        #print(packedData.hex())
        return packedData

    def printTerse(self):
        "Display the critical contents of the current object."
        print("   PR [{0:.1f},{1:.1f},{2:.1f}] az={3:.1f}, el={4:.1f} rot={5:.1f}, fc={6:d}, s={7:d}".format(self.x, self.y, self.z, self.az, self.el, self.rot, self.framecnt, self.status))

    def printVerbose(self):
        "Display all the contents of the current object."
        print("---PosRecord---")
        print("   framecnt   :", self.framecnt)
        print("   status     :", self.status)
        print("   x          :", self.x)
        print("   y          :", self.y)
        print("   z          :", self.z)
        print("   az         :", self.az)
        print("   el         :", self.el)
        print("   rot        :", self.rot)

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
        #print("---MapObjectsType---  DataLength={0:d}".format(s.size))
        #print(packedData.hex())
        return packedData

    def isActive(self):
        "Indicates whether this object is currently active."
        return self.mIsActive

    def printTerse(self):
        "Display the critical contents of the current object."
        if self.mIsActive == False:
            return
        print("   MO{0:02d} [{1:.1f},{2:.1f},{3:.1f}] id={4:d}, age={5:d}".format(self.mIndex, self.positionX, self.positionY, self.positionZ, self.classId, self.age))

    def printVerbose(self):
        "Display all the contents of the current object."
        print("---MapObjects---")
        print("   age        :", self.age)
        print("   classId    :", self.classId)
        print("   positionX  :", self.positionX)
        print("   positionY  :", self.positionY)
        print("   positionZ  :", self.positionZ)

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
        #print("---MapRecordType---  DataLength={0:d}".format(s.size))
        #print(packedData.hex())
        return packedData

    def printTerse(self):
        "Display the critical contents of the current object."
        print("   MR numBoxes={0:d}, numMaps={1:d}".format(self.boxnum, self.mapnum))
        self.posRecord.printTerse()
        for fobt in self.fifoObjBoxes:
            fobt.printTerse()
        for mo in self.mapObjs:
            mo.printTerse()

    def printVerbose(self):
        "Display all the contents of the current object."
        print("---MapRecord---")
        print("   boxnum     :", self.boxnum)
        print("   mapnum     :", self.mapnum)
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
        #print("..........")
        #print(b.hex())
        #print("..........")
        self.length = len(b)
        #self.crc32 = zlib.crc32(packedData)
        self.crc32 = zlib.crc32(b)
        s = struct.Struct('<BBBBHHI')
        packedHdr = s.pack(self.sync[0], self.sync[1], self.sync[2], self.sync[3], self.length, self.type, self.crc32)
        packedMsg = packedHdr + packedData
        print("---MapPacketType---  HdrLength={0:d}".format(s.size))
        print("  Length     : {0:04X}".format(self.length))
        print("  CalcCRC32  : {0:08X}".format(self.crc32))
        print("  ExpCRC32   : A40F6D18")
        #print(packedMsg.hex())
        return packedMsg

    def printTerse(self):
        "Display the critical contents of the current object."
        print("   MP {0:02X}{1:02X}{2:02X}{3:02X} {4:d} {5:08x}".format(self.sync[0], self.sync[1], self.sync[2], self.sync[3], self.length, self.crc32))
        self.map.printTerse()

    def printVerbose(self):
        "Display all the contents of the current object."
        print("---MapPacket---")
        print("   sync       : {0:02X} {1:02X} {2:02X} {3:02X}".format(self.sync[0], self.sync[1], self.sync[2], self.sync[3]))
        print("   length     :", self.length)
        print("   crc32      :", self.crc32)
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

def printHex(msg):
    "Display the message in a nice format."
    #print("---printHex msg---")
    print("TX :", msg.hex())
    #print("")

#------------------------------------------------------------------------------

print("")
print("...HELLO...")
print("")

try:
    brain = serial.Serial("/dev/ttyACM1", 115200, timeout=1)

    # VEX Brain request for data (it sends ASCII data currently):
    #     b'AA55CC3301\r\n'

    mpt = MapPacketType()

    msgRxCnt = 0
    while True:
        try:
            data = brain.readline()
            if data:
                msgRxCnt += 1
                print("RX :", data)
                #if (msgRxCnt % 10) == 0:
                if (msgRxCnt % 1) == 0:
                    mpt.reset()
                    mpt.setTestData()
                    #mpt.printVerbose()
                    #mpt.printTerse()
                    #print("")
                    packedMsg = mpt.getPackedMsg()
                    #print("")
                    printHex(packedMsg)
                    brain.write(packedMsg)
                    #break
        except:
            break

    brain.close()
except:
    print("***ERROR***; Couldn't open /dev/ttyACM1")


print("")
print("...BYE BYE...")
print("")

