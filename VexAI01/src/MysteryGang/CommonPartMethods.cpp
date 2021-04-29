#include "MysteryGang/CommonPartMethods.h"
#include "MysteryGang/RobotConfig.h"

namespace Cpm {
  // Set cube pull in speeds
  static int sIntakeRightMotorSpeed = 0;
  static int sIntakeLeftMotorSpeed = 0;

  void intakeCubes(unsigned int numMillisecs) {
    sIntakeLeftMotorSpeed = 150;
    sIntakeRightMotorSpeed = sIntakeLeftMotorSpeed;
    hwMotorIntakeLeft.spin(vex::directionType::rev, sIntakeLeftMotorSpeed, vex::velocityUnits::pct);
    hwMotorIntakeRight.spin(vex::directionType::fwd, sIntakeRightMotorSpeed, vex::velocityUnits::pct);
    vex::task::sleep(numMillisecs);

    stopCubeTreads();
  }

  void movePusherBackward(int rotationsInDegrees) {
    // Move pusher backward
    hwEncoderPusher.setPosition(0, degrees);
    hwMotorPusher.spin(reverse);
    while (hwEncoderPusher.position(degrees) > rotationsInDegrees) {
    } 
    stopPusher();
  }

  void movePusherForward(int rotationsInDegrees) {
    // Move pusher forward
    hwEncoderPusher.setPosition(0, degrees);
    hwMotorPusher.spin(forward);
    while (hwEncoderPusher.position(degrees) < rotationsInDegrees) {
    } 
    stopPusher();
  }

  void moveRobotBackward(int rotationsInDegrees) {
    // Move backward
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(reverse);
    hwMotorWheelBackRight.spin(reverse);
    hwMotorWheelFrontLeft.spin(reverse);
    hwMotorWheelFrontRight.spin(reverse);
    while (hwEncoderWheels.position(degrees) > rotationsInDegrees) {
    }
    stopWheels();
  }

  void moveRobotBackwardAndIntake(int rotationsInDegrees) {
    // Move backward and intake cubes
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(reverse);
    hwMotorWheelBackRight.spin(reverse);
    hwMotorWheelFrontLeft.spin(reverse);
    hwMotorWheelFrontRight.spin(reverse);
    hwMotorIntakeLeft.spin(forward);
    hwMotorIntakeRight.spin(forward);
    while (hwEncoderWheels.position(degrees) > rotationsInDegrees) {
    }
    stopWheels();
    stopCubeTreads();
  }


  void moveRobotBackwardAndOutake(unsigned int numMillisecs) {
    int leftMotorSpeed;
    int rightMotorSpeed;

    leftMotorSpeed = -50;
    rightMotorSpeed = -50;
    hwMotorWheelFrontLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct); 
    hwMotorWheelFrontRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);
    hwMotorWheelBackLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct);
    hwMotorWheelBackRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);

    sIntakeLeftMotorSpeed = -150;
    sIntakeRightMotorSpeed = sIntakeLeftMotorSpeed;
    hwMotorIntakeLeft.spin(vex::directionType::fwd, sIntakeLeftMotorSpeed, vex::velocityUnits::pct);
    hwMotorIntakeRight.spin(vex::directionType::fwd, sIntakeRightMotorSpeed, vex::velocityUnits::pct);
    vex::task::sleep(numMillisecs);

    stopWheels();
    stopCubeTreads();
  }

  void moveRobotForwardEncoders(int rotationsInDegrees) {
    // Move forward
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(forward);
    hwMotorWheelBackRight.spin(forward);
    hwMotorWheelFrontLeft.spin(forward);
    hwMotorWheelFrontRight.spin(forward);
    while (hwEncoderWheels.position(degrees) < rotationsInDegrees) {
    }

    stopWheels();
  }

  void moveRobotForwardTime(unsigned int numMillisecs) {
    // Move forward
    int leftMotorSpeed;
    int rightMotorSpeed;

    leftMotorSpeed = 150;
    rightMotorSpeed = 150;
    hwMotorWheelFrontLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct); 
    hwMotorWheelFrontRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);
    hwMotorWheelBackLeft.spin(vex::directionType::fwd, leftMotorSpeed, vex::velocityUnits::pct);
    hwMotorWheelBackRight.spin(vex::directionType::fwd, rightMotorSpeed, vex::velocityUnits::pct);
    vex::task::sleep(numMillisecs);
    
    stopWheels();
  }

  void moveRobotForwardAndIntake(int rotationsInDegrees) {
    // Move forward and intake cubes
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(forward);
    hwMotorWheelBackRight.spin(forward);
    hwMotorWheelFrontLeft.spin(forward);
    hwMotorWheelFrontRight.spin(forward);
    hwMotorIntakeLeft.spin(forward);
    hwMotorIntakeRight.spin(forward);
    while (hwEncoderWheels.position(degrees) < rotationsInDegrees) {
    }
    stopWheels();
    stopCubeTreads();
  }

  void outakeCubes(int rotationsInDegrees) {
    hwMotorIntakeLeft.setVelocity(-150, percent);
    hwMotorIntakeRight.setVelocity(-150, percent);
    hwMotorIntakeLeft.rotateFor(rotationsInDegrees, rotationUnits::deg, false);
    hwMotorIntakeRight.rotateFor(rotationsInDegrees, rotationUnits::deg);

    stopCubeTreads();
  }

  void setPusherSpeed(int pusherSpeedPercent) {
    hwMotorPusher.setVelocity(pusherSpeedPercent, percent);
  }

  void setWheelAndIntakeSpeeds(int wheelSpeedPercent, int intakeSpeedPercent) {
    hwMotorWheelBackLeft.setVelocity(wheelSpeedPercent, percent);
    hwMotorWheelBackRight.setVelocity(wheelSpeedPercent, percent);
    hwMotorWheelFrontLeft.setVelocity(wheelSpeedPercent, percent);
    hwMotorWheelFrontRight.setVelocity(wheelSpeedPercent, percent);
    hwMotorIntakeLeft.setVelocity(intakeSpeedPercent, percent);
    hwMotorIntakeRight.setVelocity(intakeSpeedPercent, percent);
  }

  void stopAllMotors() {
    stopCubeTreads();
    stopPusher();
    stopWheels();
  }
  
  void stopCubeTreads() {
    hwMotorIntakeLeft.stop();
    hwMotorIntakeRight.stop();
  }

  void stopPusher() {
    hwMotorPusher.stop();
  }

  void stopWheels() {
    hwMotorWheelFrontLeft.stop();
    hwMotorWheelFrontRight.stop();
    hwMotorWheelBackLeft.stop();
    hwMotorWheelBackRight.stop();
  }

  void turnRobotLeft(int rotationsInDegrees) {
    // Turn left
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(reverse);
    hwMotorWheelBackRight.spin(forward);
    hwMotorWheelFrontLeft.spin(reverse);
    hwMotorWheelFrontRight.spin(forward);
    while (hwEncoderWheels.position(degrees) > rotationsInDegrees) {
    }
    stopWheels();
  }

  void turnRobotRight(int rotationsInDegrees) {
    // Turn right
    hwEncoderWheels.setPosition(0, degrees);
    hwMotorWheelBackLeft.spin(forward);
    hwMotorWheelBackRight.spin(reverse);
    hwMotorWheelFrontLeft.spin(forward);
    hwMotorWheelFrontRight.spin(reverse);
    while (hwEncoderWheels.position(degrees) < rotationsInDegrees) {
    }
    stopWheels();
  }
}
