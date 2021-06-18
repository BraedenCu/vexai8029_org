#include "MysteryGang/CommonPartMethods.h"
#include "MysteryGang/ManualMode.h"
#include "MysteryGang/RobotConfig.h"
#include "Isolation.h"

extern void setJetsonDisplay(int lr);
extern void getBoxData(bool* hasTarget, int* classId, int* x, int* y, float* widthI, float* heightI, float* depthI);

static bool sHasTarget   = false;
static int   sCurClassId = 0;
static int   sCurX       = 0;
static int   sCurY       = 0;
static float sCurWidthI  = 0.0;
static float sCurHeightI = 0.0;
static float sCurDepthI  = 0.0;

static int sLeftMotorSpeed = 0;
static int sRightMotorSpeed = 0;
static int sIntakeMotorSpeed = 0;


namespace IsolationMode {

  void setWheelSpeeds() {
    const unsigned int centerX = 320;
    const int MaxSpeed = 7;  //TBD: 150;
    const int HalfSpeed = 4;  //TBD: 75;
    int targetDistance = sCurDepthI;
    int leftRight = 3;  // Default to: pointing at target

    if (sHasTarget == false) {
      sLeftMotorSpeed = 0;
      sRightMotorSpeed = 0;
      sIntakeMotorSpeed = 0;
      leftRight = 0;    // no valid target
      //Implement Search for Target
    }
    //else if (sCurX <= 130) {
    else if (sCurX <= (centerX - 100 * 2)) {
      sLeftMotorSpeed = MaxSpeed * -1;
      sRightMotorSpeed = MaxSpeed;
      sIntakeMotorSpeed = 0;
      leftRight = 1;    // Left
    }
    //else if (sCurX >= 190) {
    else if (sCurX >= (centerX + 100 * 2)) {
      sLeftMotorSpeed = MaxSpeed;
      sRightMotorSpeed = MaxSpeed * -1;
      sIntakeMotorSpeed = 0;
      leftRight = 2;    // Right
    }
    //else if (sCurX <= 155) {
    else if (sCurX <= (centerX - 60 * 2)) {
      sLeftMotorSpeed = HalfSpeed *  -1;
      sLeftMotorSpeed = HalfSpeed;
      sIntakeMotorSpeed = 0;
      leftRight = 1;    // Left
    }
    //else if (sCurX >= 165) {
    else if (sCurX >= (centerX + 60 * 2)) {
      sLeftMotorSpeed = HalfSpeed;
      sRightMotorSpeed = HalfSpeed * -1;
      sIntakeMotorSpeed = 0;
      leftRight = 2;    // Right
    }
    else {  // We are pretty much pointing at the target
      // Here the robot is pointed at the target, move forward to target
      if (targetDistance >= 30) {
        sLeftMotorSpeed = 40;
        sRightMotorSpeed = 40;
      }
      else if (targetDistance >= 16) {
        sLeftMotorSpeed = 30;
        sRightMotorSpeed = 30;
      }
      //else if (targetDistance >= 1) {
      else {
        sLeftMotorSpeed = 15;
        sRightMotorSpeed = 15;
        sIntakeMotorSpeed = 150;
      }

      //else {
        //sLeftMotorSpeed = 0;
        //sRightMotorSpeed = 0;
        //sIntakeMotorSpeed = 0;
      //}
    }
    setJetsonDisplay(leftRight);
  }

  void findNewTarget() {
    backUp(100) //back up 100 meters
    findTarget() //spin until target is found
  }

  void targetGoal(goalData) {
    setWheelSpeeds()
    if targetIsLost or distance > 50 {
      while(bumper is not pressed) {
        moveforward()
      }
    }
    while(limit switch is not pressed) {
      intakeBalls()
    }
    findNewTarget()
  }

  //-----------------------
  // Isolation mode event loop
  //-----------------------
  int isolationModeTask() {
    
    Cpm::stopAllMotors();
    
    Cpm::turnRobotLeft(90);

    // Enter the main control loop
    while (true) {
      // Get latest info on the target
      getBoxData(&sHasTarget, &sCurClassId, &sCurX, &sCurY, &sCurWidthI, &sCurHeightI, &sCurDepthI);

      setWheelSpeeds();

      // Move wheels based on trackloop positions
      hwMotorWheelFrontLeft.spin(vex::directionType::fwd, sLeftMotorSpeed, vex::velocityUnits::pct); 
      hwMotorWheelFrontRight.spin(vex::directionType::fwd, sRightMotorSpeed, vex::velocityUnits::pct);
      hwMotorWheelBackLeft.spin(vex::directionType::fwd, sLeftMotorSpeed, vex::velocityUnits::pct);
      hwMotorWheelBackRight.spin(vex::directionType::fwd, sRightMotorSpeed, vex::velocityUnits::pct);
      hwMotorIntakeLeft.spin(vex::directionType::fwd, sIntakeMotorSpeed, vex::velocityUnits::pct);
      hwMotorIntakeRight.spin(vex::directionType::fwd, sIntakeMotorSpeed, vex::velocityUnits::pct);
      hwMotorIntakeLifter.spin(vex::directionType::rev, sIntakeMotorSpeed, vex::velocityUnits::pct);
      hwMotorPusher.spin(vex::directionType::rev, sIntakeMotorSpeed, vex::velocityUnits::pct);

      // Short delay just in case we want to display something on the controller
      //vex::task::sleep(1);
    }
  }
}
