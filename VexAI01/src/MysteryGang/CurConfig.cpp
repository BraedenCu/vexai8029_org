#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CurConfig.h"
#include "MysteryGang/ManualMode.h"
#include "MysteryGang/RobotConfig.h"

namespace CurConfig {
  //-----------------------
  // Local Variables
  //-----------------------
  const char* sOverallBuildDate = __DATE__;
  const char* sOverallBuildTime = __TIME__;
  const char* sOverallVersion   = "0003";

  static AutonAlgoType       sAutonAlgo          = AUTON_ALGO_4_PT;
  static GameModeType        sGameMode           = GAME_MODE_ALLIANCE;
  static ProtectionSideType  sProtectionSide     = PROTECTION_SIDE_UNPROTECTED;
  static StartingSideType    sStartingSide       = STARTING_SIDE_RIGHT;

  static AutonAlgoType       sTmpAutonAlgo       = sAutonAlgo;
  static GameModeType        sTmpGameMode        = sGameMode;
  static ProtectionSideType  sTmpProtectionSide  = sProtectionSide;
  static StartingSideType    sTmpStartingSide    = sStartingSide;

  static unsigned int sSelectionIndex = 100;  // Start out of range so it is zero on first use

  //-----------------------
  // Local function prototypes
  //-----------------------
  char* getAutonAlgoStr();
  char* getGameModeStr();
  char* getProtectionSideStr();
  char* getStartingSideStr();

  //--------------------------------------------------------------------------------
  // Process the down arrow button press (Exit config without saving)
  void buttonDownPressed() {
    if (hwCompetition.isEnabled() == true) {
      return;
    }

    hwController.Screen.clearScreen();
    hwController.Screen.setCursor(1,1);
    hwController.Screen.print("Exiting Config");
    vex::task::sleep(1000);

    // Cancelling out of configuration change mode, revert all tmps back
    sTmpAutonAlgo         = sAutonAlgo;
    sTmpGameMode          = sGameMode;
    sTmpProtectionSide    = sProtectionSide;
    sTmpStartingSide      = sStartingSide;

    displayConfigController();
    sSelectionIndex = 100;
  }

  // Process the left arrow button press (Select item)
  void buttonLeftPressed() {
    if (hwCompetition.isEnabled() == true) {
      return;
    }

    switch (sSelectionIndex) {
      case 0  :  sTmpGameMode          = GAME_MODE_ALLIANCE;            break;
      case 1  :  sTmpGameMode          = GAME_MODE_SKILLS;              break;
      case 2  :  sTmpProtectionSide    = PROTECTION_SIDE_PROTECTED;     break;
      case 3  :  sTmpProtectionSide    = PROTECTION_SIDE_UNPROTECTED;   break;
      case 4  :  sTmpStartingSide      = STARTING_SIDE_LEFT;            break;
      case 5  :  sTmpStartingSide      = STARTING_SIDE_RIGHT;           break;
      case 6  :  sTmpAutonAlgo         = AUTON_ALGO_1_PT;               break;
      case 7  :  sTmpAutonAlgo         = AUTON_ALGO_4_PT;               break;
      case 8  :  sTmpAutonAlgo         = AUTON_ALGO_5_PT;               break;
      case 9  :  sTmpAutonAlgo         = AUTON_ALGO_8_PT;               break;
      default :  return;
    }

    hwController.Screen.clearScreen();
    hwController.Screen.setCursor(1,1);
    hwController.Screen.print("Item Selected");
    vex::task::sleep(1000);
  }

  // Process the right arrow button press (Next item)
  void buttonRightPressed() {
    if (hwCompetition.isEnabled() == true) {
      return;
    }

    sSelectionIndex++;
    if (sSelectionIndex > 9) {
      sSelectionIndex = 0;
    }

    hwController.Screen.clearScreen();
    hwController.Screen.setCursor(1,1);

    switch (sSelectionIndex) {
      case 0  :  hwController.Screen.print("GM A");    break;
      case 1  :  hwController.Screen.print("GM S");    break;
      case 2  :  hwController.Screen.print("PM P");    break;
      case 3  :  hwController.Screen.print("PM U");    break;
      case 4  :  hwController.Screen.print("SS L");    break;
      case 5  :  hwController.Screen.print("SS R");    break;
      case 6  :  hwController.Screen.print("AA 1");    break;
      case 7  :  hwController.Screen.print("AA 4");    break;
      case 8  :  hwController.Screen.print("AA 5");    break;
      case 9  :  hwController.Screen.print("AA 8");    break;
      default :  break;
    }
  }

  // Process the up arrow button press (Save config)
  void buttonUpPressed() {
    if (hwCompetition.isEnabled() == true) {
      return;
    }

    // Save configuration change
    sAutonAlgo      = sTmpAutonAlgo;
    sGameMode       = sTmpGameMode;
    sProtectionSide = sTmpProtectionSide;
    sStartingSide   = sTmpStartingSide;

    hwController.Screen.clearScreen();
    hwController.Screen.setCursor(1,1);
    hwController.Screen.print("Saving Config");
    vex::task::sleep(1000);

    displayConfigController();
    sSelectionIndex = 100;
  }

  void displayConfigBrain() {
    hwBrain.Screen.clearScreen();
    hwBrain.Screen.setCursor(1,1);
    // Diisplay overall information (build date and time, version, etc.)
    //    OV : Overall Version
    hwBrain.Screen.print("OV=%s : %s [%s]", sOverallVersion, sOverallBuildDate, sOverallBuildTime);
    hwBrain.Screen.newLine();

    char* gameModeStr = getGameModeStr();

    // Display Driver Control info
    //    DV : Driver Version
    //    GM : Game Mode (Alliance/Skills)
    const char* driverVersionStr = ManualMode::getVersion();
    const char* driverBuildDateStr = ManualMode::getBuildDate();
    const char* driverBuildTimeStr = ManualMode::getBuildTime();
    hwBrain.Screen.print("DV=%s : %s [%s]", driverVersionStr, driverBuildDateStr, driverBuildTimeStr);
    hwBrain.Screen.newLine();
    hwBrain.Screen.print("GM=%s", gameModeStr);
    hwBrain.Screen.newLine();

    char* autonAlgoStr = getAutonAlgoStr();
    char* protectionSideStr = getProtectionSideStr();
    char* startingSideStr = getStartingSideStr();

    // Display Autonomous info
    //    AV : Auton Version
    //    AA : Auton Algo 1,4,8 pt
    //    PS : Protection Side (Protected/Unprotected)
    //    SS : Starting Side (Left/Right)
    const char* autonVersionStr = AutonMode::getVersion();
    const char* autonBuildDateStr = AutonMode::getBuildDate();
    const char* autonBuildTimeStr = AutonMode::getBuildTime();
    hwBrain.Screen.print("AV=%s : %s [%s]", autonVersionStr, autonBuildDateStr, autonBuildTimeStr);
    hwBrain.Screen.newLine();
    hwBrain.Screen.print("GM=%s, AA=%s, PS=%s, SS=%s", gameModeStr, autonAlgoStr, protectionSideStr, startingSideStr);
  }

  void displayConfigController() {
    hwController.Screen.clearScreen();
    hwController.Screen.setCursor(1,1);
    // Display Autonomous info
    //    AV  :  Auton Version
    //    AA  :  Auton Algo 1,4,8 pt
    //    PS  :  Protection Side (Protected/Unprotected)
    //    SS  :  Starting Side (Left/Right)
    char* autonAlgoStr = getAutonAlgoStr();
    char* gameModeStr = getGameModeStr();
    char* protectionSideStr = getProtectionSideStr();
    char* startingSideStr = getStartingSideStr();
    const char* autonVersionStr = AutonMode::getVersion();
    const char* autonBuildDateStr = AutonMode::getBuildDate();

    hwController.Screen.print("AV=%s : %s", autonVersionStr, autonBuildDateStr);
    hwController.Screen.newLine();
    hwController.Screen.print("GM=%s, AA=%s", gameModeStr, autonAlgoStr);
    hwController.Screen.newLine();
    hwController.Screen.print("PS=%s, SS=%s", protectionSideStr, startingSideStr);
  }

  AutonAlgoType getAutonAlgo() {
    return sAutonAlgo;
  }

  char* getAutonAlgoStr() {
    switch (sAutonAlgo) {
      case AUTON_ALGO_1_PT    :  return (char*)"1";
      case AUTON_ALGO_4_PT    :  return (char*)"4";
      case AUTON_ALGO_5_PT    :  return (char*)"5";
      case AUTON_ALGO_8_PT    :  return (char*)"8";
      default                 :  return (char*)"?";
    }
  }

  GameModeType getGameMode() {
    return sGameMode;
  }

  char* getGameModeStr() {
    switch (sGameMode) {
      case GAME_MODE_ALLIANCE    :  return (char*)"A";
      case GAME_MODE_SKILLS      :  return (char*)"S";
      default                    :  return (char*)"?";
    }
  }

  ProtectionSideType getProtectionSide() {
    return sProtectionSide;
  }

  char* getProtectionSideStr() {
    switch (sProtectionSide) {
      case PROTECTION_SIDE_PROTECTED      :  return (char*)"P";
      case PROTECTION_SIDE_UNPROTECTED    :  return (char*)"U";
      default                             :  return (char*)"?";
    }
  }

  StartingSideType getStartingSide() {
    return sStartingSide;
  }

  char* getStartingSideStr() {
    switch (sStartingSide) {
      case STARTING_SIDE_LEFT   :  return (char*)"L";
      case STARTING_SIDE_RIGHT  :  return (char*)"R";
      default                   :  return (char*)"?";
    }
  }

  void initialize() {
    // Register for the Up, Down, Left, Right group of Arrow buttons
    hwController.ButtonDown.pressed(buttonDownPressed);
    hwController.ButtonLeft.pressed(buttonLeftPressed);
    hwController.ButtonRight.pressed(buttonRightPressed);
    hwController.ButtonUp.pressed(buttonUpPressed);
  }
}
