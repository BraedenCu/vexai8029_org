#include "vex.h"
#include "MysteryGang/RobotConfig.h"

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

  Brain.Screen.setClipRegion( ox, oy, width, height);
  Brain.Screen.setFont( mono15 );
  // border and titlebar
  Brain.Screen.setPenColor( yellow );
  Brain.Screen.drawRectangle(ox, oy, width, height, black );
  Brain.Screen.drawRectangle( ox, oy, width, 20, grey );

  Brain.Screen.setPenColor( yellow );
  Brain.Screen.setFillColor( grey );
  Brain.Screen.printAt(ox + 10, oy + 15, "Jetson" );
  oy += 20;
  
  Brain.Screen.setPenColor( white );
  Brain.Screen.setFillColor( black );
  
  // get last map data
  jetson_comms.get_data( &local_map );

  Brain.Screen.printAt( ox + 10, oy += 15, "Packets   %d", jetson_comms.get_packets() );
  Brain.Screen.printAt( ox + 10, oy += 15, "Errors    %d", jetson_comms.get_errors() );
  Brain.Screen.printAt( ox + 10, oy += 15, "Timeouts  %d", jetson_comms.get_timeouts() );
  Brain.Screen.printAt( ox + 10, oy += 15, "data/sec  %d             ", total_data );
  Brain.Screen.printAt( ox + 10, oy += 15, "pkts/sec  %d             ", total_packets );
  Brain.Screen.printAt( ox + 10, oy += 15, "boxnum    %d", local_map.boxnum );
  Brain.Screen.printAt( ox + 10, oy += 15, "mapnum    %d", local_map.mapnum );
  Brain.Screen.printAt( ox + 10, oy += 15, "RxCRC     %x", jetson_comms.getPayloadCrc32()); //<cdo>
  Brain.Screen.printAt( ox + 10, oy += 15, "CalcCRC   %x", jetson_comms.getCalcCrc32()); //<cdo>

  // once per second, update data rate stats
  if( Brain.Timer.system() > update_time ) {
    update_time = Brain.Timer.system() + 1000;
    total_data = jetson_comms.get_total() - last_data;
    total_packets = jetson_comms.get_packets() - last_packets;
    last_data = jetson_comms.get_total();
    last_packets = jetson_comms.get_packets();
  }
  
  Brain.Screen.setFont( mono12 );
  for(int i=0;i<4;i++ ) {
    if( i < local_map.boxnum ) {
      Brain.Screen.printAt( ox + 10, oy += 12, "box %d: c:%d x:%d y:%d w:%d h:%d depth:%.1f",i,
                           (local_map.boxobj[i].classID), //Class ID (0 = Red 1 = Blue 2 = Goal)
                           (local_map.boxobj[i].x), //in pixels
                           (local_map.boxobj[i].y), //in pixels
                           (local_map.boxobj[i].width), //in pixels
                           (local_map.boxobj[i].height), //in pixels
                           (local_map.boxobj[i].depth));
    }
    else {
      Brain.Screen.printAt( ox + 10, oy += 12, "---");
    }
  }
  for(int i=0;i<4;i++ ) {
    if( i < local_map.mapnum ) {
      Brain.Screen.printAt( ox + 10, oy += 12, "map %d: a:%4d c:%4d X:%.2f Y:%.2f Z:%.1f",i,
                           local_map.mapobj[i].age,
                           local_map.mapobj[i].classID,
                           (local_map.mapobj[i].positionX / -25.4),  // mm -> inches
                           (local_map.mapobj[i].positionY / -25.4),  // mm -> inches
                           (local_map.mapobj[i].positionZ / 25.4)); // mm -> inches
    }
    else {
      Brain.Screen.printAt( ox + 10, oy += 12, "---");
    }
  }

}

//
// Task to update screen with status
//
int dashboardTask() {
  while(true) {
    // status
    //dashboardJetson();
    dashboardJetson(    0, 0, 280, 240 );
    // draw, at 30Hz
    Brain.Screen.render();
    this_thread::sleep_for(16*100);
  }
  return 0;
}