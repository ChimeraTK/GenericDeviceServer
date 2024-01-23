// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#pragma once

#include <ChimeraTK/ApplicationCore/ApplicationCore.h>
#include <ChimeraTK/ApplicationCore/PeriodicTrigger.h>
#include <ChimeraTK/ApplicationCore/ScriptedInitialisationHandler.h>
#ifdef WITH_DAQ
#  include <ChimeraTK/ApplicationCore/MicroDAQ.h>
#endif

namespace ctk = ChimeraTK;

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

#ifdef WITH_DAQ
  ctk::MicroDAQ<uint64_t> daq;
  void initialise() override;
#endif
};
