// SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
// SPDX-License-Identifier: LGPL-3.0-or-later

#pragma once

#include <ChimeraTK/ApplicationCore/ApplicationCore.h>
#include <ChimeraTK/ApplicationCore/PeriodicTrigger.h>
#include <ChimeraTK/ApplicationCore/ScriptedInitialisationHandler.h>
#include <ChimeraTK/DataConsistencyGroup.h>

namespace ctk = ChimeraTK;


struct FindMax : public ctk::ApplicationModule {
  using ctk::ApplicationModule::ApplicationModule;
  ChimeraTK::ArrayPushInput<int32_t> signal{this, "/ADC/channels/signal10", "", 16384, "DAQ0 channel 10"};
  ChimeraTK::ScalarOutput<uint32_t> maxPos{this, "maxPos", "", ""};
  void mainLoop() override {
    // device is already initialized and current input values loaded
    while(true) {
      maxPos = std::max_element(signal.begin(), signal.end())-signal.begin();
      writeAll();
      readAll();
    }
  }
};
struct ConsistentEvaluation : public ctk::ApplicationModule {
  using ctk::ApplicationModule::ApplicationModule;
  ChimeraTK::ArrayPushInput<int32_t> signal{this, "/ADC/channels/signal10", "", 16384, "DAQ0 channel 10"};
  ChimeraTK::ScalarPushInput<uint32_t> maxPos{this, "maxPos", "", ""};
  ChimeraTK::ScalarOutput<int32_t> maxVal{this, "maxVal", "", ""};
  ChimeraTK::ScalarOutput<uint32_t> consistentSamples{this, "consistentSamples", "", ""};
  ChimeraTK::ScalarOutput<uint32_t> inconsistentSamples{this, "inconsistentSamples", "", ""};
  const int maxValExpected = 999;
  void mainLoop() override {
    auto rag = readAnyGroup();
    auto dcg = ctk::DataConsistencyGroup({signal, maxPos});
    while(true) {
      auto elementId = rag.readAny();
      if (dcg.update(elementId)) {
        if (maxVal == maxValExpected){
          consistentSamples++;
        } else {
          inconsistentSamples++;
        }
      }
      writeAll();
    }
  }
};

struct GenericApp : public ctk::Application {
  GenericApp();
  ~GenericApp() override;

  std::vector<ctk::PeriodicTrigger> periodicTriggers;

  struct DeviceModuleGroup : public ctk::ModuleGroup {
    DeviceModuleGroup(ctk::ModuleGroup* owner, std::string alias, std::string triggerPath, std::string pathInDevice,
        std::string initScript);
    ctk::DeviceModule _deviceModule;
    std::unique_ptr<ctk::ScriptedInitHandler> initHandler;
  };

  std::vector<DeviceModuleGroup> deviceModules;

  FindMax sc{this, "FindMax", ""};
  ConsistentEvaluation ce{this, "ConsistentEvaluation", ""};
};


