#include <ChimeraTK/ApplicationCore/ApplicationCore.h>
#include <ChimeraTK/ApplicationCore/PeriodicTrigger.h>
#include <ChimeraTK/ApplicationCore/EnableXMLGenerator.h>
#include <ChimeraTK/ApplicationCore/ScriptedInitialisationHandler.h>

namespace ctk = ChimeraTK;

struct GenericApp : public ctk::Application {
  GenericApp() : Application("generic_device_server") {
    ChimeraTK::setDMapFilePath("devices.dmap");
  }
  ~GenericApp() { shutdown(); }
  ctk::ConfigReader config{this, "Config","generic-device-server_configuration.xml", {}};
  std::vector<ctk::PeriodicTrigger> periodicTriggers;
  struct ConnectingDeviceModuleGroup : public ctk::ModuleGroup{
    ConnectingDeviceModuleGroup(ctk::EntityOwner* owner, std::string alias,
      std::string triggerPath, std::string pathInDevice, std::string initScript) :
      ModuleGroup(owner, alias, ""),
      _deviceModule(this, alias, triggerPath, nullptr, pathInDevice) {
        if (!initScript.empty()) {
          initHandler = std::make_unique<ctk::ScriptedInitHandler> (this, "", "", initScript, _deviceModule.getDeviceModule());
        }
      }
    ctk::ConnectingDeviceModule _deviceModule;
    std::unique_ptr <ctk::ScriptedInitHandler> initHandler;
  };
  std::vector<ConnectingDeviceModuleGroup> connectingDeviceModules;
  void defineConnections() override;
};
static GenericApp theGenericApp;


void GenericApp::defineConnections() {

  std::vector<std::string> timers = config.get<std::vector<std::string>>("periodicTimers");
  for (const std::string& timer : timers) {
    periodicTriggers.emplace_back(ctk::PeriodicTrigger(this, timer, "Periodic timer", config.get<uint32_t>(timer+"/period")));
  }

  std::vector<std::string> devices = config.get<std::vector<std::string>>("devices");
  for (const std::string& device : devices) {
    connectingDeviceModules.emplace_back(this, device,
    config.get<std::string>(device+"/triggerPath"),
    config.get<std::string>(device+"/pathInDevice"),
    config.get<std::string>(device+"/initScript")
    );
  }

  Application::defineConnections();
  //dumpConnections();
}
