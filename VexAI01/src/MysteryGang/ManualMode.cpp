#include "MysteryGang/CommonPartMethods.h"
#include "MysteryGang/ManualMode.h"
#include "MysteryGang/RobotConfig.h"

namespace ManualMode {
  //-----------------------
  // Local Variables
  //-----------------------
  const char* sBuildDate = __DATE__;
  const char* sBuildTime = __TIME__;
  const char* sVersion   =   "0003";

  // Wheel speed adjustment variable
  static int sDivisor = 1;

  // Set cube pull in speeds
  static int sIntakeRightMotorSpeed = 0;
  static int sIntakeLeftMotorSpeed = 0;

  // Set cube pull in lifter speed
  static int sLifterMotorSpeed = 0;

  // Set cube holder pusher speed
  static int sPusherMotorSpeed = 0;

  //-----------------------
  // Function Prototypes
  //-----------------------
  void registerEventHandlers();

  //-----------------------
  // Manual mode event loop
  //-----------------------

  void enterManualControl() {
    int leftMotorSpeed;
    int rightMotorSpeed;
    
    Cpm::stopAllMotors();
    registerEventHandlers();

    // Enter the main control loop
    while (true) {
      // Set wheel speeds
      leftMotorSpeed = hwController.Axis3.value() / sDivisor;
      rightMotorSpeed = hwController.Axis2.value() / sDivisor;

      // Move wheels based on joystick positions
      hwMotorWheelFrontLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct); 
      hwMotorWheelFrontRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);
      hwMotorWheelBackLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct);
      hwMotorWheelBackRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);

      // Move cube pull in treads based on buttonL1
      hwMotorIntakeLeft.spin(vex::directionType::fwd, sIntakeLeftMotorSpeed, vex::velocityUnits::pct);
      hwMotorIntakeRight.spin(vex::directionType::fwd, sIntakeRightMotorSpeed, vex::velocityUnits::pct);

      // Move cube push out treads based on buttonY
      hwMotorIntakeLeft.spin(vex::directionType::rev, sIntakeLeftMotorSpeed, vex::velocityUnits::pct);
      hwMotorIntakeRight.spin(vex::directionType::rev, sIntakeRightMotorSpeed, vex::velocityUnits::pct);

      // Move cube pull in lifter based on buttonA/B
      hwMotorIntakeLifter.spin(vex::directionType::fwd, sLifterMotorSpeed, vex::velocityUnits::pct);

      // Move pusher based on buttonR1/R2
      hwMotorPusher.spin(vex::directionType::fwd, sPusherMotorSpeed, vex::velocityUnits::pct);

      // Short delay just in case we want to display something on the controller
      vex::task::sleep(1);
    }
  }

  //-----------------------
  // Event handlers
  //-----------------------

  // When button x is pressed, change the wheel speed
  void buttonXpressed() {
    if (sDivisor == 1) {
      sDivisor = 5;
    }
    else {
      sDivisor = 1;
    }
  }

  // Activate cube pull in
  void buttonL1Pressed() {
    sIntakeRightMotorSpeed = -150;
    sIntakeLeftMotorSpeed = -150;
  }

  // Stop cube pull in
  void buttonL1Released() {
    sIntakeRightMotorSpeed = 0;
    sIntakeLeftMotorSpeed = 0;
  }

  // Activate cube push out
  void buttonL2Pressed() {
    sIntakeRightMotorSpeed = 150;
    sIntakeLeftMotorSpeed = 150;
  }

  // Stop cube push out
  void buttonL2Released() {
    sIntakeRightMotorSpeed = 0;
    sIntakeLeftMotorSpeed = 0;
  }

  // Activate pusher forwards
  void buttonR1Pressed() {
    sPusherMotorSpeed = 150;
  }

  // Stop pusher forwards
  void buttonR1Released() {
    sPusherMotorSpeed = 0;
  }

  // Activate pusher back
  void buttonR2Pressed() {
    sPusherMotorSpeed = -150;
  }

  // Stop pusher back
  void buttonR2Released() {
    sPusherMotorSpeed = 0;
  }

  // Pull lifter up
  void buttonAPressed() {
    sLifterMotorSpeed = 150;
  }

  // Stop lifter
  void buttonAReleased() {
    sLifterMotorSpeed = 0;
  }

  // Push lifter down
  void buttonBPressed() {
    sLifterMotorSpeed = -150;
  }

  // Stop lifter
  void buttonBReleased() {
    sLifterMotorSpeed = 0;
  }

  const char* getBuildDate() {
    return sBuildDate;
  }
  
  const char* getBuildTime() {
    return sBuildTime;
  }

  const char* getVersion() {
    return sVersion;
  }

  void registerEventHandlers() {
    // Register event handlers for button A,B,X,Y, L1,L2, R1,R2

    // Register for the A,B,X,Y group of buttons
    hwController.ButtonA.pressed(buttonAPressed);
    hwController.ButtonA.released(buttonAReleased);
    hwController.ButtonB.pressed(buttonBPressed);
    hwController.ButtonB.released(buttonBReleased);
    hwController.ButtonX.pressed(buttonXpressed);
    //hwController.ButtonY.pressed(buttonYpressed);

    // Register for the L1,L2 group of buttons
    hwController.ButtonL1.pressed(buttonL1Pressed);
    hwController.ButtonL1.released(buttonL1Released);
    hwController.ButtonL2.pressed(buttonL2Pressed);
    hwController.ButtonL2.released(buttonL2Released);

    // Register for the R1,R2 group of buttons
    hwController.ButtonR1.pressed(buttonR1Pressed);
    hwController.ButtonR1.released(buttonR1Released);
    hwController.ButtonR2.pressed(buttonR2Pressed);
    hwController.ButtonR2.released(buttonR2Released);
  }
}
