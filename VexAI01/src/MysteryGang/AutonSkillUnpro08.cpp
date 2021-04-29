#include "vex.h"
#include "MysteryGang/RobotConfig.h"
#include "MysteryGang/CurConfig.h"
#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CommonPartMethods.h"





namespace AutonSkillsUnpro08 {
  //-----------------------------------
  //--- Local prototypes
  //-----------------------------------
  void performAlgoLeft();
  void performAlgoRight();


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
      // TODO - Finish
      break;
    }
  }

  //--------------------------------------------------------------------------------
  void performAlgoLeft() {
    // Unfold robot
    Cpm::moveRobotBackwardAndOutake(1250);
    vex::task::sleep(100);

    Cpm::setWheelAndIntakeSpeeds(50,100);
    Cpm::setPusherSpeed(100);

    Cpm::moveRobotForwardAndIntake(1080*2);
    vex::task::sleep(200);

    Cpm::moveRobotBackwardAndIntake(-360);
    vex::task::sleep(200);

    Cpm::turnRobotLeft(-107);
    vex::task::sleep(200);

    Cpm::moveRobotForwardEncoders(422);
    vex::task::sleep(200);

    // Correct position of the bottom cube
    Cpm::outakeCubes(200);
    vex::task::sleep(200);

    // Push cube tray upright
    Cpm::movePusherForward(270);
    vex::task::sleep(200);

    // Correct position of the bottom cube
    Cpm::intakeCubes(300);
    vex::task::sleep(200);

    // Push cube holder down
    Cpm::movePusherBackward(-135);
    vex::task::sleep(200);

    // Move backward while outaking cubes in order to stack cubes in the corner
    Cpm::moveRobotBackwardAndOutake(750);
  }

  //--------------------------------------------------------------------------------
  void performAlgoRight() {
  }
}
