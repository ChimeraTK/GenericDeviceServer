// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#include "GenericApp.h"

GenericApp::DeviceModuleGroup::DeviceModuleGroup(ctk::ModuleGroup* owner, std::string alias, std::string triggerPath,
    std::string pathInDevice, std::string initScript)
: ModuleGroup(owner, alias, ""), _deviceModule(this, alias, triggerPath, nullptr, pathInDevice) {
  if(!initScript.empty()) {
    initHandler = std::make_unique<ctk::ScriptedInitHandler>(this, "", "", initScript, _deviceModule);
  }
}

GenericApp::GenericApp() : Application("generic_chimeratk_server") {
  ChimeraTK::setDMapFilePath("devices.dmap");

  auto& config = appConfig();
  std::vector<std::string> timers = config.get<std::vector<std::string>>("periodicTimers");
  for(const std::string& timer : timers) {
    periodicTriggers.emplace_back(
        ctk::PeriodicTrigger(this, timer, "Periodic timer", config.get<uint32_t>(timer + "/period")));
  }

  std::vector<std::string> devices = config.get<std::vector<std::string>>("devices");
  for(const std::string& device : devices) {
    deviceModules.emplace_back(this, device, config.get<std::string>(device + "/triggerPath"),
        config.get<std::string>(device + "/pathInDevice"), config.get<std::string>(device + "/initScript"));
  }
}

GenericApp::~GenericApp() {
  shutdown();
}
