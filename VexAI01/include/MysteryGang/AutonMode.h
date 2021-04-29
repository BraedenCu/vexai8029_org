#ifndef AutonMode_h
#define AutonMode_h

namespace AutonMode {
  void enterAutonomousControl();
  const char* getBuildDate();
  const char* getBuildTime();
  const char* getVersion();
}

namespace Auton01 {
  void performAlgo();
}

namespace AutonAlliPro04 {
  void performAlgo();
}

namespace AutonAlliUnpro04 {
  void performAlgo();
}

namespace AutonAlliUnpro05 {
  void performAlgo();
}

namespace AutonSkillsUnpro08 {
  void performAlgo();
}

#endif