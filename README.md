# Generic Device Server

The Generic Device Server is a simple ApplicationCore Server that supports
exposing devices to a control system. Simple application logic, such as value
conversions, can be achieved using a
[LogicalNameMapped device](https://chimeratk.github.io/ChimeraTK-DeviceAccess/head/html/lmap.html)
and the [math plugin](https://chimeratk.github.io/ChimeraTK-DeviceAccess/head/html/lmap.html#plugins_reference_math)

## Building

TBD

## Configuration

The configuration of the generic device server, in its simplest form, needs a 
device map (DMAP) file and a server configuration file.

However, additional configuration files for the chosen control system adapter
might be necessary.

### The DMAP file

The DMAP file has to be named `devices.dmap`.
It provides a mapping of name aliases to device addresses. For the full
description of the format, see
https://chimeratk.github.io/DeviceAccess/master/dmap.html. The aliases will be
used in the configuration file.

### The server configuration file

This file controls which devices are exposed to the control system.
It has to be named `generic_chimeratk_server_configuration.xml`. The full
description of the configuration format can be found at
https://chimeratk.github.io/ApplicationCore/master/configreader.html

The server configuration file has to define two variables:

- `devices`, which is a list of device aliases from `devices.dmap` which
  should be connected.

- `periodicTimers`, which is a list of name for timers. Timers can be used to
  trigger periodic read-out of pollable devices.

Both, devices and timers, need further configuration.

This configuration is done creating a `<module>` with the name of the device or
timer, and further detailing the part 

#### Device configuration

A device configuration needs to be further detailed out, specifying the
following parameters

- `triggerPath`, a string describing a variable path which, when written to,
  will trigger a read-out of the device. This can either be an arbitrary path
  which is then exposed to the control system and can be written to manually, or
  a path to a previously configured timer's `tick` output, for periodic read-out.
- `pathInDevice`, a string specifying which part of the device should be
  exposed, or all of it, by using either `"/"` or the empty string `""`.
- `initScript`, a path in the file system pointing to a program that will be run
  whenever a device might need some initialisation sequence, such as server
  start up or error recovery. It is up to the script to detect whether it needs
  to actually do anything or not. It can be left empty, `""`, if no such script
  is needed.

#### Trigger configuration

A trigger can be configured using

- `interval` , a 32bit unsigned integer, which specifies the time between ticks
  in milliseconds.

#### Walkthrough of a full example

The code snippets below are taken from the XML file in the `sample_configs`
folder in this repository.

First, we start with the usual XML declaration and root tag.:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<configuration>
```

We then declare that we want to connect two devices, `TMCB1` and `TMCB2` and
have one periodic timer that is called `msTimer`.

```xml
  <variable name="devices" type="string">
    <value i="0"  v="TMCB1"/>
    <value i="1"  v="TMCB2"/>
  </variable>

  <variable name="periodicTimers" type="string">
    <value i="0"  v="msTimer"/>
  </variable>
```

The timer should run every 1000 milliseconds

```xml
  <module name="msTimer">
    <variable name="period" type="uint32" value="1000" />
  </module>
```

For the device `TMCB1`, we want it to be read out once a second using the
`msTimer` trigger, but are only interested in the `BSP` part of the device. Upon
start or recovery, we need to do additional initialisation of the device using
a script called `writeWordStatus`, which is located next to the server binary.

```xml
 <module name="TMCB1">
    <variable name="triggerPath" type="string" value="/msTimer/tick" />
    <variable name="pathInDevice" type="string" value="/BSP" />
    <variable name="initScript" type="string" value="./writeWordStatus" />
 </module>
```

The device TMCB2, on the other hand, shall only be read on manual request, for
example if someone might click on a button in the user interface of the control
system. Therefore we set the trigger path to `/manual/trigger`. We want to
expose the whole device and do not need any additional initialisation, so we
configure those empty.

```xml
  <module name="TMCB2">
    <variable name="triggerPath" type="string" value="/manual/trigger" />
    <variable name="pathInDevice" type="string" value="" />
    <variable name="initScript" type="string" value="" />
 </module>
```

And then we just close off the file.

```xml
</configuration>
```

### Python integration

For integrating python application modules into the generic server setup, refer
to [the commented python example in the ApplicationCore documentation](https://chimeratk.github.io/ChimeraTK-ApplicationCore/head/html/example_python_modules.html)

### Configuring the control system

The configuration file for the control system depends on the chosen control
system adapter. If no file is provided, it will default to expose everything to
the control system.

#### DOOCS

DOOCS requires you to set up a server configuration file named `doocs-generic-chimeratk-server01.conf`.

Additional configuration of variable mapping can be done through the DOOCS variable mapping file. It has to be named
`generic_chimeratk_server-DoocsVariableConfig.xml`.

For details on both, refer to the [documentation of the DOOCS
control system adapter](https://chimeratk.github.io/ChimeraTK-ControlSystemAdapter-DoocsAdapter/head/html/index.html#Integration)

#### EPICS

TBD

#### OPC-UA

The mapping file for OPC-UA has to be named
`generic_chimeratk_server_mapping.xml`.

For further details on the format, refer to the [example configuration](https://github.com/ChimeraTK/ControlSystemAdapter-OPC-UA-Adapter/blob/master/opcuaAdapter_mapping.xml)

#### TANGO

The mapping file for TANGO has to be named `tango-generic-chimeratk-server02-AttributeMapper.xml`, or more specifically the name of the executable.
For details on the file format, refer to [the AttributeMapper documentation](https://chimeratk.github.io/ChimeraTK-ControlSystemAdapter-TangoAdapter/head/html/index.html#attribute_mapping)
