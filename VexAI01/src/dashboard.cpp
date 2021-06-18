#include "vex.h"
#include "MysteryGang/RobotConfig.h"

static vex::mutex sBoxLock;
static int   sCurClassId = 0;
static int   sCurX       = 0;
static int   sCurY       = 0;
static float sCurWidthI  = 0.0;
static float sCurHeightI = 0.0;
static float sCurDepthI  = 0.0;
static bool  sHasTargets = false;

static int sLeftRight = 0;      //lr: 0=notDetected | 1=left | 2=right | 3=onTarget

void setJetsonDisplay(int lr) {
  sLeftRight = lr;
}

void getBoxData(bool* hasTarget, int* classId, int* x, int* y, float* widthI, float* heightI, float* depthI) {
  sBoxLock.lock();
  *classId    = sCurClassId;
  *x          = sCurX;
  *y          = sCurY;
  *widthI     = sCurWidthI;
  *heightI    = sCurHeightI;
  *depthI     = sCurDepthI;
  *hasTarget  = sHasTargets;
  sBoxLock.unlock();
}

static void setBoxData(int classId, int x, int y, float widthI, float heightI, float depthI) {
  sBoxLock.lock();
  sCurClassId = classId;
  sCurX       = x;
  sCurY       = y;
  sCurWidthI  = widthI;
  sCurHeightI = heightI;
  sCurDepthI  = depthI;
  if (widthI == 0.0) {
    sHasTargets = false;
  }
  else {
    sHasTargets = true;
  }
  sBoxLock.unlock();
}

//
// Display various useful information about the Jetson
//
static void dashboardJetson() {
  static int counter = 0;
  static MAP_RECORD  local_map;

  counter++;

  hwBrain.Screen.clearScreen();
  hwBrain.Screen.setCursor(1,1);

  // get last map data
  jetson_comms.get_data( &local_map );

  hwBrain.Screen.print("%d: Hello from dashboard", counter);
  hwBrain.Screen.newLine();

  hwBrain.Screen.print("  Packets   : %d", jetson_comms.get_packets() );
  hwBrain.Screen.newLine();
  hwBrain.Screen.print("  numBoxes  : %d", local_map.boxnum);
  hwBrain.Screen.newLine();
  hwBrain.Screen.print("  numMaps   : %d", local_map.mapnum);
  hwBrain.Screen.newLine();
}

static void
dashboardJetson( int ox, int oy, int width, int height ) {
  static int32_t     last_data = 0;
  static int32_t     last_packets = 0;
  static int32_t     total_data = 0;
  static int32_t     total_packets = 0;
  static uint32_t    update_time = 0;
  static MAP_RECORD  local_map;
  color grey = vex::color(0x404040);

#if 0
  Brain.Screen.setClipRegion( ox, oy, width, height);
  Brain.Screen.setFont( mono15 );
  // border and titlebar
  Brain.Screen.setPenColor( yellow );
  Brain.Screen.drawRectangle(ox, oy, width, height, black );
  Brain.Screen.drawRectangle( ox, oy, width, 20, grey );

  Brain.Screen.setPenColor( yellow );
  Brain.Screen.setFillColor( grey );
  Brain.Screen.printAt(ox + 10, oy + 15, "Jetson" );
#endif
  oy += 20;
  
#if 0
  Brain.Screen.setPenColor( white );
  Brain.Screen.setFillColor( black );
#endif

  // get last map data
  jetson_comms.get_data( &local_map );

#if 0
  Brain.Screen.printAt( ox + 10, oy += 15, "Packets   %d", jetson_comms.get_packets() );
  Brain.Screen.printAt( ox + 10, oy += 15, "Errors    %d", jetson_comms.get_errors() );
  Brain.Screen.printAt( ox + 10, oy += 15, "Timeouts  %d", jetson_comms.get_timeouts() );
  Brain.Screen.printAt( ox + 10, oy += 15, "data/sec  %d             ", total_data );
  Brain.Screen.printAt( ox + 10, oy += 15, "pkts/sec  %d             ", total_packets );
  Brain.Screen.printAt( ox + 10, oy += 15, "boxnum    %d", local_map.boxnum );
  Brain.Screen.printAt( ox + 10, oy += 15, "mapnum    %d", local_map.mapnum );
  Brain.Screen.printAt( ox + 10, oy += 15, "RxCRC     %x", jetson_comms.getPayloadCrc32()); //<cdo>
  Brain.Screen.printAt( ox + 10, oy += 15, "CalcCRC   %x", jetson_comms.getCalcCrc32()); //<cdo>
#endif

  // once per second, update data rate stats
  if( Brain.Timer.system() > update_time ) {
    update_time = Brain.Timer.system() + 1000;
    total_data = jetson_comms.get_total() - last_data;
    total_packets = jetson_comms.get_packets() - last_packets;
    last_data = jetson_comms.get_total();
    last_packets = jetson_comms.get_packets();
  }
  
  Brain.Screen.setFont( mono12 );
  float widthI = 0.0;
  float heightI = 0.0;
  float depthI = 0.0;
  bool hasValidTarget = false;
  for(int i=0;i<4;i++ ) {
    if( i < local_map.boxnum ) {
      widthI = local_map.boxobj[i].width / 25.4;
      heightI = local_map.boxobj[i].height / 25.4;
      depthI = local_map.boxobj[i].depth / 25.4;
#if 0
      Brain.Screen.printAt( ox + 10, oy += 12, "box %d: c:%d x:%d y:%d w:%.1f h:%.1f d:%.1f",i,
                           local_map.boxobj[i].classID, //Class ID (0 = Red 1 = Blue 2 = Goal)
                           local_map.boxobj[i].x, //in pixels
                           local_map.boxobj[i].y, //in pixels
                           widthI,
                           heightI,
                           depthI);
#endif
      const unsigned int RED_BALL = 0;
      const unsigned int BLUE_BALL = 1;
      if (local_map.boxobj[i].classID == RED_BALL) {
        hasValidTarget = true;
        setBoxData(local_map.boxobj[i].classID,
                    local_map.boxobj[i].x, local_map.boxobj[i].y,
                    widthI, heightI, depthI);        
      }
    }
    else {
#if 0
      Brain.Screen.printAt( ox + 10, oy += 12, "---");
#endif
    }
  }
  if (hasValidTarget == false) {
    setBoxData(1, 0, 0, 0.0, 0.0, 0.0);
  }
  for(int i=0;i<4;i++ ) {
    if( i < local_map.mapnum ) {
#if 0
      Brain.Screen.printAt( ox + 10, oy += 12, "map %d: a:%4d c:%4d X:%.2f Y:%.2f Z:%.1f",i,
                           local_map.mapobj[i].age,
                           local_map.mapobj[i].classID,
                           (local_map.mapobj[i].positionX / -25.4),  // mm -> inches
                           (local_map.mapobj[i].positionY / -25.4),  // mm -> inches
                           (local_map.mapobj[i].positionZ / 25.4)); // mm -> inches
#endif
    }
    else {
#if 0
      Brain.Screen.printAt( ox + 10, oy += 12, "---");
#endif
    }
  }

}

//
// Display various useful information about VEXlink
//
static void dashboardVexlink( int ox, int oy, int width, int height ) {
  static int32_t last_data = 0;
  static int32_t last_packets = 0;
  static int32_t total_data = 0;
  static int32_t total_packets = 0;
  static uint32_t update_time = 0;  

  color darkred = vex::color(0x800000);
  color darkgrn = vex::color(0x008000);

#if 0
  Brain.Screen.setClipRegion( ox, oy, width, height);
  Brain.Screen.setFont( mono15 );

  // border and titlebar
  Brain.Screen.setPenColor( yellow );
  Brain.Screen.drawRectangle(ox, oy, width, height, black );
  Brain.Screen.drawRectangle( ox, oy, width, 20 );

  // Link status in titlebar
  Brain.Screen.setPenColor(darkred);
  Brain.Screen.setFillColor(darkred);
  Brain.Screen.drawRectangle( ox+1, oy+1, width-2, 18 );
  Brain.Screen.setPenColor(yellow);
  Brain.Screen.printAt(ox + 10, oy + 15, "VEXlink: Disconnected" );
#endif
  oy += 20;

  // get last map data
  static MAP_RECORD  local_map;
  jetson_comms.get_data( &local_map );
#if 0
typedef struct {
	int32_t		framecnt;       // This counter increments each frame
	int32_t		status;         // 0 = All Good, != 0 = Not All Good
	float	    x, y, z;        // X,Y,Z field coordinates in millimeters. Position 0,0 is in the middle of the field.
                            // Z is mm from the field tiles.
                            // NOTE: These coordinates are for the GPS sensor (FLIR Camera) If you want to know the location of the 
                            // center of your robot you will have add an offset. 
	float	    az;             // Rotation of the robot in radians (Heading)
  float     el;             // Elevation of the robot in radians (Pitch)
  float     rot;            // Rotation/Tilt of the robot in radians (Roll)
} POS_RECORD;
#endif

  char lr = '-';
  if (sLeftRight == 3) {
    lr = 'T';
  }
  else if (sLeftRight == 1) {
    lr = 'L';
  }
  else if (sLeftRight == 2) {
    lr = 'R';
  }
  Brain.Screen.setFillColor(black);
  Brain.Screen.setPenColor(white);
#if 0
  Brain.Screen.printAt( ox + 10, oy += 15, "FrameCnt  %d", local_map.pos.framecnt );
  Brain.Screen.printAt( ox + 10, oy += 15, "Status    %d", local_map.pos.status );
  Brain.Screen.printAt( ox + 10, oy += 15, "x         %d", int(local_map.pos.x) );
  Brain.Screen.printAt( ox + 10, oy += 15, "y         %d", int(local_map.pos.y));
  Brain.Screen.printAt( ox + 10, oy += 15, "z         %d", int(local_map.pos.z));
  Brain.Screen.printAt( ox + 10, oy += 15, "az        %d", int(local_map.pos.az) );
  Brain.Screen.printAt( ox + 10, oy += 15, "el        %d", int(local_map.pos.el));
  Brain.Screen.printAt( ox + 10, oy += 15, "rot       %d", int(local_map.pos.rot));
  Brain.Screen.printAt( ox + 10, oy += 15, "L/R       %c", lr);
#endif
}

//
// Task to update screen with status
//
int dashboardTask() {
  while(true) {
    // status
    //dashboardJetson();
    dashboardJetson(    0, 0, 280, 240 );
    dashboardVexlink( 279, 0, 201, 240 );
    // draw, at 30Hz
#if 0
    Brain.Screen.render();
#endif
    //this_thread::sleep_for(16*100);
    this_thread::sleep_for(16);
  }
  return 0;
}