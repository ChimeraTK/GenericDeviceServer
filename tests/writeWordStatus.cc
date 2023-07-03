#include <ChimeraTK/Device.h>

int main() {
  ChimeraTK::setDMapFilePath("devices.dmap");

  ChimeraTK::Device d("ADC_BOARD");
  d.open();
  d.write("/BSP/BOOT_STATUS/DUMMY_WRITEABLE", 42);
}
