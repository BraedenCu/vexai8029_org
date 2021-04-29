#include "vex.h"
#include "MysteryGang/AutonMode.h"
#include "MysteryGang/CommonPartMethods.h"
#include "MysteryGang/CurConfig.h"

namespace AutonMode {
  //-----------------------
  // Local Variables
  //-----------------------
  const char* sBuildDate = __DATE__;
  const char* sBuildTime = __TIME__;
  const char* sVersion = "0003";

  //-----------------------
  // Local function prototypes
  //-----------------------
  void enterAlliance();
  void enterAllianceProtected();
  void enterAllianceUnprotected();
  void enterSkills();
  void enterSkillsProtected();
  void enterSkillsUnprotected();

  //--------------------------------------------------------------------------------
  void enterAlliance() {
    CurConfig::ProtectionSideType protectionSide = CurConfig::getProtectionSide();
  
    switch (protectionSide) {
    case CurConfig::PROTECTION_SIDE_PROTECTED :
      enterAllianceProtected();
      break;
    case CurConfig::PROTECTION_SIDE_UNPROTECTED :
      enterAllianceUnprotected();
      break;
    default :
      // TODO - Finish
      break;
    }
  }

  void enterAllianceProtected() {
    CurConfig::AutonAlgoType algo = CurConfig::getAutonAlgo();

    switch (algo) {
    case CurConfig::AUTON_ALGO_1_PT :
      Auton01::performAlgo();
      break;
    case CurConfig::AUTON_ALGO_4_PT :
      AutonAlliPro04::performAlgo();
      break;
    default :
      // TODO - Finish
      break;
    }
  }

  void enterAllianceUnprotected() {
    CurConfig::AutonAlgoType algo = CurConfig::getAutonAlgo();

    switch (algo) {
    case CurConfig::AUTON_ALGO_1_PT :
      Auton01::performAlgo();
      break;
    case CurConfig::AUTON_ALGO_4_PT :
      AutonAlliUnpro04::performAlgo();
      break;
    case CurConfig::AUTON_ALGO_5_PT :
      AutonAlliUnpro05::performAlgo();
      break;
    default :
      // TODO - Finish
      break;
    }
  }

  void enterAutonomousControl() {
    CurConfig::GameModeType gameMode = CurConfig::getGameMode();
  
    Cpm::stopAllMotors();

    switch (gameMode) {
    case CurConfig::GAME_MODE_SKILLS :
      enterSkills();
      break;
    case CurConfig::GAME_MODE_ALLIANCE :
      enterAlliance();
      break;
    default :
      // TODO - Finish
      break;
    }

    // Wait forever so autonomous doesn't start up again
    vex::task::sleep(0xffffffff);
  }

  void enterSkills() {
    CurConfig::ProtectionSideType protectionSide = CurConfig::getProtectionSide();
  
    switch (protectionSide) {
    case CurConfig::PROTECTION_SIDE_PROTECTED :
      enterSkillsProtected();
      break;
    case CurConfig::PROTECTION_SIDE_UNPROTECTED :
      enterSkillsUnprotected();
      break;
    default :
      // TODO - Finish
      break;
    }
  }

  void enterSkillsProtected() {
    CurConfig::AutonAlgoType algo = CurConfig::getAutonAlgo();

    switch (algo) {
    case CurConfig::AUTON_ALGO_8_PT :
      //TODO  AutonSkillsPro08::performAlgo();
      break;
    default :
      // TODO - Finish
      break;
    }
  }

  void enterSkillsUnprotected() {
    CurConfig::AutonAlgoType algo = CurConfig::getAutonAlgo();

    switch (algo) {
    case CurConfig::AUTON_ALGO_8_PT :
      AutonSkillsUnpro08::performAlgo();
      break;
    default :
      // TODO - Finish
      break;
    }
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
}
