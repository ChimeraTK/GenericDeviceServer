// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#pragma once

#include <ChimeraTK/ApplicationCore/ApplicationCore.h>
#include <ChimeraTK/ApplicationCore/PeriodicTrigger.h>
#include <ChimeraTK/ApplicationCore/ScriptedInitialisationHandler.h>

namespace ctk = ChimeraTK;

struct LogicExample : public ctk::ApplicationModule {
  using ctk::ApplicationModule::ApplicationModule;
  ChimeraTK::ArrayPushInput<uint32_t> timingCnt{this, "/ADC_LOGICAL/timing/triggerCnt", "", 4, "hw trigger counters"};
  ChimeraTK::ScalarOutput<std::string> status{this, "status", "(no unit)", "fpga app status"};
  ChimeraTK::ScalarOutput<uint32_t> loopCounter{this, "loopCounter", "", ""};

  void mainLoop() override {
    // device is already initialized and current input values loaded
    uint32_t lastCnt = 0;
    while(true) {
      status = timingCnt[1] != lastCnt ? "fpga app running" : "fpga app not running";
      lastCnt = timingCnt[1];
      loopCounter++;
      writeAll();

      readAll();
    }
  }
};

struct GenericApp : public ctk::Application {
  GenericApp();
  ~GenericApp() override;

  ctk::ConfigReader config{this, "Config", getName() + "_configuration.xml"};
  std::vector<ctk::PeriodicTrigger> periodicTriggers;

  struct DeviceModuleGroup : public ctk::ModuleGroup {
    DeviceModuleGroup(ctk::ModuleGroup* owner, std::string alias, std::string triggerPath, std::string pathInDevice,
        std::string initScript);
    ctk::DeviceModule _deviceModule;
    std::unique_ptr<ctk::ScriptedInitHandler> initHandler;
  };

  std::vector<DeviceModuleGroup> deviceModules;

  LogicExample sc{this, "logicExample", ""};
};
