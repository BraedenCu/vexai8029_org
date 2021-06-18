#include "vex.h"
#include "MysteryGang/RobotConfig.h"
#include "MysteryGang/CurConfig.h"
#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CommonPartMethods.h"





  //-----------------------------------
  //--- Local prototypes
  //-----------------------------------
  void driveForward();
  //void performAlgoRight();

  //--------------------------------------------------------------------------------
  void driveForward() {
    Cpm::setWheelAndIntakeSpeeds(50,0);
    //Cpm::setPusherSpeed(100);

    Cpm::moveRobotForwardTime(500);
    vex::task::sleep(200);

   }
