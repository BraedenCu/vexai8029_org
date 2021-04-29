#ifndef CurConfig_h
#define CurConfig_h

namespace CurConfig {

  //-----------------------
  // Types and enumerations
  //-----------------------
  enum AutonAlgoType {
    AUTON_ALGO_1_PT,
    AUTON_ALGO_4_PT,
    AUTON_ALGO_5_PT,
    AUTON_ALGO_8_PT
  };

  // Current type of game mode (skills or alliance)
  enum GameModeType {
    GAME_MODE_ALLIANCE,
    GAME_MODE_SKILLS
  };

  // Current protection side (protected or unprotected)
  enum ProtectionSideType {
    PROTECTION_SIDE_PROTECTED,
    PROTECTION_SIDE_UNPROTECTED
  };

  // Current starting side (left or right)
  enum StartingSideType {
    STARTING_SIDE_LEFT,
    STARTING_SIDE_RIGHT
  };

  //-----------------------
  // Function Prototypes
  //-----------------------

  // Displays the current version and configuration to the brain screen
  void displayConfigBrain();

  // Displays the current version and configuration to the controller screen
  void displayConfigController();

  // Get the current configuration autonomous algorithm (1,4,5,8 points)
  AutonAlgoType getAutonAlgo();

  // Get the current configuration autonomous game mode (alliance or skills)
  GameModeType getGameMode();

  // Get the current configuration autonomous protection side (protected or unprotected)
  ProtectionSideType getProtectionSide();

  // Get the current configuration autonomous starting side (left or right)
  StartingSideType getStartingSide();
  
  // Initialize the configuration
  void initialize();
}

#endif
