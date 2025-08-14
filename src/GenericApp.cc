// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#include "GenericApp.h"

#include <ChimeraTK/Exception.h>

GenericApp::DeviceModuleGroup::DeviceModuleGroup(ctk::ModuleGroup* owner, std::string alias, std::string triggerPath,
    std::string pathInDevice, std::string initScript)
: ModuleGroup(owner, alias, ""), _deviceModule(this, alias, triggerPath, nullptr, pathInDevice) {
  if(!initScript.empty()) {
    initHandler = std::make_unique<ctk::ScriptedInitHandler>(this, "", "", initScript, _deviceModule);
  }
}

GenericApp::GenericApp() : Application("generic_chimeratk_server") {
  ChimeraTK::setDMapFilePath("devices.dmap");

  if(std::getenv("GENERIC_SERVER_DEBUG_CONNECTIONS") != nullptr) {
    debugMakeConnections();
    ctk::Logger::getInstance().setMinSeverity(ctk::Logger::Severity::debug);
  }

  auto& config = appConfig();
  std::vector<std::string> timers;
  try {
    timers = config.get<std::vector<std::string>>("periodicTimers");
  }
  catch(const ctk::logic_error&) {
    // No periodic timers entry, nothing to do. Just catch the exception and leave the list empty.
  }
  for(const std::string& timer : timers) {
    periodicTriggers.emplace_back(this, timer, "Periodic timer", config.get<uint32_t>(timer + "/period"));
  }

  std::vector<std::string> devices;
  try {
    devices = config.get<std::vector<std::string>>("devices");
  }
  catch(const ctk::logic_error&) {
    // No devices, nothing to do. Just catch the exception and leave the list empty.
  }
  for(const std::string& device : devices) {
    deviceModules.emplace_back(this, device, config.get<std::string>(device + "/triggerPath"),
        config.get<std::string>(device + "/pathInDevice"), config.get<std::string>(device + "/initScript"));
  }
}

GenericApp::~GenericApp() {
  shutdown();
}
