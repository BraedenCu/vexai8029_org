#include "MysteryGang/RobotConfig.h"

// VEXcode device constructors
vex::brain       hwBrain;
vex::competition hwCompetition;
vex::controller  hwController           = vex::controller(primary);
vex::encoder     hwEncoderPusher        = vex::encoder(hwBrain.ThreeWirePort.E);
vex::encoder     hwEncoderWheels        = vex::encoder(hwBrain.ThreeWirePort.A);
vex::encoder     hwEncoderGh            = vex::encoder(hwBrain.ThreeWirePort.G);
vex::motor       hwMotorWheelFrontLeft  = vex::motor(PORT7, ratio18_1, true);
vex::motor       hwMotorWheelFrontRight = vex::motor(PORT6, ratio18_1, false);
vex::motor       hwMotorWheelBackLeft   = vex::motor(PORT5, ratio18_1, true);
vex::motor       hwMotorWheelBackRight  = vex::motor(PORT8, ratio18_1, false);
vex::motor       hwMotorIntakeLeft      = vex::motor(PORT20, ratio18_1, false);
vex::motor       hwMotorIntakeRight     = vex::motor(PORT2, ratio18_1, true);
vex::motor       hwMotorIntakeLifter    = vex::motor(PORT11, ratio18_1, false);
vex::motor       hwMotorPusher          = vex::motor(PORT1, ratio18_1, true);
