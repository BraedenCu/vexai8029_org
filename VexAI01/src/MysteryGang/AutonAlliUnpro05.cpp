/*---------------------------------------------------------------------------*/
/*                  Autonomous Alliance Unprotected 5 Cubes                  */
/*---------------------------------------------------------------------------*/

#include "MysteryGang/RobotConfig.h"
#include "MysteryGang/CurConfig.h"
#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CommonPartMethods.h"

namespace AutonAlliUnpro05 {
  //-----------------------
  // Local prototypes
  //-----------------------
  void performAlgoLeft();
  void performAlgoRight();

  //--------------------------------------------------------------------------------
  void performAlgo() {
    CurConfig::StartingSideType startingSide = CurConfig::getStartingSide();

    switch (startingSide) {
    case CurConfig::STARTING_SIDE_LEFT :
        performAlgoLeft();
        break;
    case CurConfig::STARTING_SIDE_RIGHT :
        performAlgoRight();
        break;
    default :
        // TBD - Finish
        break;
    }
  }

  //--------------------------------------------------------------------------------
  void performAlgoLeft() {
    // Push preload cube out of the way
    Cpm::moveRobotForwardEncoders(360);

    // Unfold robot
    Cpm::moveRobotBackwardAndOutake(1250);
    vex::task::sleep(100);

    Cpm::setWheelAndIntakeSpeeds(50,100);

    Cpm::moveRobotForwardAndIntake(1120);
    vex::task::sleep(200);

    Cpm::moveRobotBackwardAndIntake(-400);
    vex::task::sleep(200);

    Cpm::turnRobotLeft(-400);
    vex::task::sleep(200);

    Cpm::moveRobotForwardEncoders(380);
    vex::task::sleep(200);

    // Correct position of the bottom cube
    Cpm::outakeCubes(-201);
    vex::task::sleep(200);

    // Push cube tray upright
    Cpm::setPusherSpeed(100);
    Cpm::movePusherForward(370);
    vex::task::sleep(200);

    // Straighten out the stack
    Cpm::moveRobotForwardTime(420);
    vex::task::sleep(200);

    // Lift bottom of the pusher high enough to clear the ledge
    Cpm::movePusherBackward(-155);
    vex::task::sleep(200);

    // Move backward while outaking cubes in order to stack cubes in the corner
    Cpm::moveRobotBackwardAndOutake(1000);
  }

  //--------------------------------------------------------------------------------
  void performAlgoRight() {
    // Push preload cube out of the way
    Cpm::moveRobotForwardEncoders(360);

    // Unfold robot
    Cpm::moveRobotBackwardAndOutake(1250);
    vex::task::sleep(100);

    Cpm::setWheelAndIntakeSpeeds(50,100);

    Cpm::moveRobotForwardAndIntake(1120);
    vex::task::sleep(200);

    Cpm::moveRobotBackwardAndIntake(-400);
    vex::task::sleep(200);

    Cpm::turnRobotRight(400);
    vex::task::sleep(200);

    Cpm::moveRobotForwardEncoders(380);
    vex::task::sleep(200);

    // Correct position of the bottom cube
    Cpm::outakeCubes(-195);
    vex::task::sleep(200);

    // Push cube tray upright
    Cpm::setPusherSpeed(100);
    Cpm::movePusherForward(370);
    vex::task::sleep(200);

    // Straighten out the stack
    Cpm::moveRobotForwardTime(420);
    vex::task::sleep(200);

    // Lift bottom of the pusher high enough to clear the ledge
    Cpm::movePusherBackward(-155);
    vex::task::sleep(200);

    // Move backward while outaking cubes in order to stack cubes in the corner
    Cpm::moveRobotBackwardAndOutake(1000);
  }
}
