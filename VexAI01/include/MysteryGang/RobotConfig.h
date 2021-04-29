#ifndef RobotConfig_h
#define RobotConfig_h

#include "vex.h"


// VEXcode devices
extern vex::brain       hwBrain;
extern vex::competition hwCompetition;
extern vex::controller  hwController;
extern vex::encoder     hwEncoderPusher;
extern vex::encoder     hwEncoderWheels;
extern vex::encoder     hwEncoderGh;  // Currently unused, encoder attached to right wheel
extern vex::motor       hwMotorWheelFrontLeft;
extern vex::motor       hwMotorWheelFrontRight;
extern vex::motor       hwMotorWheelBackLeft;
extern vex::motor       hwMotorWheelBackRight;
extern vex::motor       hwMotorIntakeLeft;
extern vex::motor       hwMotorIntakeRight;
extern vex::motor       hwMotorIntakeLifter;
extern vex::motor       hwMotorPusher;

#endif
