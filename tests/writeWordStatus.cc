#include <ChimeraTK/Device.h>

int main() {
  ChimeraTK::setDMapFilePath("devices.dmap");

  ChimeraTK::Device d("TMCB1");
  d.open();
  d.write("/BSP/WORD_STATUS/DUMMY_WRITEABLE", 42);
}
