#ifndef CommonPartMethods_h
#define CommonPartMethods_h

namespace Cpm {
  // Move treads to pull in cubes for the specified amount of time
  void intakeCubes(unsigned int numMillisecs);

  // Pull the cube stacker tray down backwards for the specified motor rotations
  // Rotations in degrees must be negative
  void movePusherBackward(int rotationsInDegrees);

  // Push the cube stacker tray up forwards for the specified motor rotations
  // Rotations in degrees must be positive
  void movePusherForward(int rotationsInDegrees);

  // Move the robot backwards for the specified motor rotations
  // Rotations in degrees must be negative
  void moveRobotBackward(int rotationsInDegrees);

  // Move the robot backwards for the specified motor rotations and move treads to pull in cubes at the same time
  // Rotations in degrees must be negative
  void moveRobotBackwardAndIntake(int rotationsInDegrees);

  // Move the robot backwards and move treads to push out cube at the same time for the specified amount of time
  void moveRobotBackwardAndOutake(unsigned int numMillisecs);

  // Move the robot forwards for the specified motor rotations
  // Rotations in degrees must be positive
  void moveRobotForwardEncoders(int rotationsInDegrees);

  // Move the robot forwards for the specified amount of time
  void moveRobotForwardTime(unsigned int numMillisecs);

  // Move the robot forwards for the specified motor rotations and move treads to pull in cubes at the same time
  void moveRobotForwardAndIntake(int rotationsInDegrees);

  // Move treads to push out cubes for the specified motor rotations
  // Rotations in degrees must be negative
  void outakeCubes(int rotationsInDegrees);

  // Set the cube stacker tray motor speeds
  void setPusherSpeed(int pusherSpeedPercent);

  // Set the wheel and cube tread motor speeds
  void setWheelAndIntakeSpeeds(int wheelSpeedPercent, int intakeSpeedPercent);

  // Stop all of the robot's motors
  void stopAllMotors();

  // Stop the cube pull in/push out treads
  void stopCubeTreads();

  // Stop the cube stacker tray
  void stopPusher();

  // Stop the robot's wheels
  void stopWheels();

  // Turn the robot to the left for the specified motor rotations
  // Rotations in degrees must be negative
  void turnRobotLeft(int rotationsInDegrees);

  // Turn the robot to the right for the specified motor rotations
  // Rotations in degrees must be positive
  void turnRobotRight(int rotationsInDegrees);
}

#endif
