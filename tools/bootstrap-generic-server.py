#!/usr/bin/env python3

# SPDX-FileCopyrightText: Deutsches Elektronen-Synchrotron DESY, MSK, ChimeraTK Project <chimeratk-support@desy.de>
# SPDX-License-Identifier: LGPL-3.0-or-later

import argparse
import deviceaccess as da
import lxml.etree as ET
import os.path
import socket
import typing


def _pretty_write_xml(root, file):
    print("<?xml version='1.0' encoding='utf-8'?>", file=file)
    tree = ET.ElementTree(root)
    ET.indent(tree)
    print(ET.tostring(tree, encoding="utf-8").decode('utf-8'), file=file)


class XLMapper:
    # Convert a RegisterCataloge into a configuration file for logical name mapping
    def __init__(self, target_device: str):
        self.tree = {"children": {}, "register": None}
        self.target_device = target_device

    def map_catalogue(self, catalogue):
        for r in catalogue:
            path = r.getRegisterName()[1:].split('/')
            self._recursive_add(path, self.tree, r)

    def _recursive_add(self, path: list[str], tree, register_info):
        if len(path) > 0:
            if path[0] not in tree["children"]:
                tree["children"][path[0]] = {"children": {}, "register": None}

            self._recursive_add(path[1:], tree["children"][path[0]], register_info)
        else:
            tree["register"] = register_info

    def write(self, file: typing.TextIO) -> str:
        root = ET.Element('logicalNameMap')
        self._build_xml(root, self.tree)
        _pretty_write_xml(root, file)

    def _build_xml(self, element: ET.Element, tree):
        v = tree["register"]
        if v:
            k = v.getRegisterName().split("/")[-1]
            if v.getNumberOfDimensions() < 2:
                register = ET.SubElement(element, "redirectedRegister", attrib={"name": k})
                ET.SubElement(register, "targetDevice").text = self.target_device
                ET.SubElement(register, "targetRegister").text = v.getRegisterName()
            else:
                for i in range(0, v.getNumberOfChannels()):
                    channel = ET.SubElement(element, "redirectedChannel", attrib={"name": f"{k}_{i}"})
                    ET.SubElement(channel, "targetDevice").text = self.target_device
                    ET.SubElement(channel, "targetRegister").text = v.getRegisterName()
                    ET.SubElement(channel, "targetChannel").text = str(i)

        for k, v in tree["children"].items():
            sub_tree = ET.SubElement(element, "module", attrib={"name": k})
            self._build_xml(sub_tree, v)


class ServerConfig:
    def __init__(self, device_list, python_modules):
        self.root = ET.Element('configuration')
        devices = ET.SubElement(self.root, 'variable', attrib={"name": "devices", "type": "string"})
        for index, device_name in enumerate(device_list):
            ET.SubElement(devices, 'value', attrib={"i": str(index), "v": device_name})
            device_entry = ET.SubElement(self.root, 'module', attrib={"name": device_name})
            ET.SubElement(device_entry, 'variable', attrib={
                          "name": "triggerPath", "type": "string", "value": "/msTimer/tick"})
            ET.SubElement(device_entry, 'variable', attrib={"name": "pathInDevice", "type": "string", "value": "/"})
            init_script = f"{device_name}Init.py"
            ET.SubElement(device_entry, 'variable', attrib={
                          "name": "initScript", "type": "string", "value": f"./{init_script}"})
            if not os.path.exists(init_script):
                with open(init_script, "w+") as f:
                    print(f"""#!/usr/bin/env python3

import deviceaccess as da
import sys

try:
    da.setDMapFilePath("device.dmap")
    device = da.Device("{device_name}_unmapped")
    device.open()
    # device.write("APP.RESET_N", 1)
    sys.exit(0)
except Exception as e:
    print(e)
    sys.exit(1)
""", file=f)
                    os.chmod(init_script, 0o755)

        timer = ET.SubElement(self.root, 'variable', attrib={"name": "periodicTimers", "type": "string"})
        ET.SubElement(timer, 'value', attrib={"i": str(index), "v": "msTimer"})

        timer_module = ET.SubElement(self.root, 'module', attrib={"name": "msTimer"})
        ET.SubElement(timer_module, 'variable', attrib={"name": "period", "type": "uint32", "value": "100"})

        if python_modules:
            py_modules = ET.SubElement(self.root, 'module', attrib={"name": 'PythonModules'})

            for module in python_modules:
                module_group = ET.SubElement(py_modules, 'module', attrib={"name": module})
                ET.SubElement(module_group, 'variable', attrib={"name": "path", "type": "string", "value": module})

            # check if user passed us an existing python file, if not: create a simple template
            if not os.path.exists(module + ".py"):
                with open(module + ".py", 'w+') as f:
                    print(f"""
import PyApplicationCore as ac

class {module}(ac.ApplicationModule):
    def __init__(self, owner):
        super().__init__(owner, "{module}", "Please add description here")

    def mainLoop(self):
        # Implementation goes here
        pass

ac.app.{module} = {module}(ac.app)
                          """, file=f)

    def write(self):
        with open('generic_device_server-config.xml', 'w') as f:
            _pretty_write_xml(self.root, f)


class DOOCS:
    def __init__(self, catalogue, args):
        self.catalogue = catalogue
        self.facility, self.device, self.location = args.doocs_address.split("/")
        self.hostname = args.hostname
        self.rpc_number = args.doocs_rpc_number
        self.mapped_device = args.device_name

    def write_config(self):
        with open('doocs-generic-chimeratk-server02.conf', 'w+') as f:
            print(f"""
eq_conf:

oper_uid:       -1
oper_gid:       1000
xpert_uid:      0
xpert_gid:      0
ring_buffer:    10000
memory_buffer:  500

eq_fct_name:    "{self.hostname}._SVR"
eq_fct_type:    1
{{
SVR.RPC_NUMBER:         {self.rpc_number}
SVR.NAME:       "{self.hostname}._SVR"
SVR.BPN:        6000
SVR.FACILITY: "{self.facility}"
SVR.DEVICE: "{self.device}"
}}
""", file=f)

    def write_mapping(self):
        root = ET.Element("{https://github.com/ChimeraTK/ControlSystemAdapter-DoocsAdapter}device_server")
        location = ET.SubElement(root, "location", attrib={"name": self.location})
        ET.SubElement(location, "import").text = "/" + self.mapped_device
        location = ET.SubElement(root, "location", attrib={"name": "Debug"})
        ET.SubElement(location, "import").text = "/"
        with open("generic_chimeratk_server-DoocsVariableConfig.xml", "w+") as f:
            _pretty_write_xml(root, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mapfile", help="Path to a firmware register map file")
    parser.add_argument('--device-name', default='DEV0', help="Name of the exposed device. (default: %(default)s)")
    parser.add_argument('--mapped-device-file', default=None,
                        help="The name of the XLMAP file. Will be derived from --device-name if not given explicitly",
                        type=argparse.FileType('w', encoding='utf-8'))
    parser.add_argument('--adapter', default='DOOCS', choices=['TANGO', 'DOOCS', 'OPC-UA'],
                        help="Control system framework integration to generate (default: %(default)s)")
    parser.add_argument('--add-python-module', default=[], nargs='+', dest="python_modules",
                        help="Generate code for including python modules into the configuration")
    parser.add_argument('--hostname', default=socket.gethostname().upper(),
                        help="DOOCS: Hostname to use for configuration (default: %(default)s)")
    parser.add_argument(
        '--doocs-address', default=None, help="DOOCS: Address in the form of Facility/Device/Location. If not given, defaults to TEST.DOOCS/LOCALHOST_610498009/device-name")
    parser.add_argument('--doocs-rpc-number', default='610498009',
                        help="DOOCS: The RPC number to use (default: %(default)s)")
    args = parser.parse_args()

    # Generate the dynamic defaults
    if not args.mapped_device_file:
        args.mapped_device_file = open(f"{args.device_name}.xlmap", "w", encoding="utf-8")

    if not args.doocs_address:
        args.doocs_address = f"TEST.DOOCS/LOCALHOST_610498009/{args.device_name}"

    print('Generating DMAP file')
    with open('devices.dmap', 'w') as f:
        print(f'{args.device_name}_unmapped (dummy?map={args.mapfile})', file=f)
        print(f'{args.device_name} (logicalNameMap?map={args.mapped_device_file.name})', file=f)

    print('Generating configuration for generic server')
    config = ServerConfig([args.device_name], args.python_modules)
    config.write()

    print('Creating basic logical name mapping config')
    device = da.Device(f'(dummy?map={args.mapfile})')
    catalogue = device.getRegisterCatalogue()
    mapper = XLMapper(args.device_name + "_unmapped")
    mapper.map_catalogue(catalogue)
    mapper.write(args.mapped_device_file)

    print(f'Generating configuration for adapter type {args.adapter}')
    if args.adapter == 'DOOCS':
        d = DOOCS(catalogue, args)
        d.write_config()
        d.write_mapping()
