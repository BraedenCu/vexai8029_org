/*---------------------------------------------------------------------------*/
/*      Autonomous, Alliance or Skills, Unprotected or Protected, 1 Cube     */
/*---------------------------------------------------------------------------*/

#include "vex.h"
#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CommonPartMethods.h"

namespace Auton01 {
  //--------------------------------------------------------------------------------
  void performAlgo() {
    // Unfold robot for use in user control
    Cpm::moveRobotBackwardAndOutake(1250);
    vex::task::sleep(100);

    Cpm::setWheelAndIntakeSpeeds(50,100);

    // Push cube into corner
    Cpm::moveRobotBackward(500);
    vex::task::sleep(200);

    // Move robot away from cube
    Cpm::moveRobotForwardEncoders(500);
  }
}
