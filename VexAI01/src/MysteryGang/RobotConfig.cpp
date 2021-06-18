#include "MysteryGang/RobotConfig.h"

// VEXcode device constructors
vex::brain       hwBrain;
vex::competition hwCompetition;
vex::controller  hwController           = vex::controller(primary);
vex::encoder     hwEncoderPusher        = vex::encoder(hwBrain.ThreeWirePort.E);
vex::encoder     hwEncoderWheels        = vex::encoder(hwBrain.ThreeWirePort.A);
vex::encoder     hwEncoderGh            = vex::encoder(hwBrain.ThreeWirePort.G);
vex::motor       hwMotorWheelFrontLeft  = vex::motor(PORT11, ratio18_1, false);
vex::motor       hwMotorWheelFrontRight = vex::motor(PORT13, ratio18_1, true);
vex::motor       hwMotorWheelBackLeft   = vex::motor(PORT12, ratio18_1, false);
vex::motor       hwMotorWheelBackRight  = vex::motor(PORT14, ratio18_1, true);
vex::motor       hwMotorIntakeLeft      = vex::motor(PORT16, ratio18_1, false);
vex::motor       hwMotorIntakeRight     = vex::motor(PORT17, ratio18_1, true);
vex::motor       hwMotorIntakeLifter    = vex::motor(PORT18, ratio18_1, true);
vex::motor       hwMotorPusher          = vex::motor(PORT19, ratio18_1, true);

extern bumper BumperC;
