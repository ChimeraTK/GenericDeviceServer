import os

DEVICE_ALIAS_REG = "device_reg"

def create_dmap(slot, reg_map_file, dummy_mode: bool):
    """creates dmap file with given slot and map files.

    :param slot: slot in MicroTCA Crate
    :type slot: int
    :param reg_map_file: .map file pointer
    :type reg_map_file: string
    :param dummy_mode: If you want to run this script against a dummy backend use True
    :type dummy_mode: bool
    """
    if not os.path.exists("./include/temp.dmap"):
        os.mknod("./include/temp.dmap")

    with open("./include/temp.dmap", "w") as dmap_file:
        # Path of the map file inside the dmap has to be where the REAL script is run

        if dummy_mode:  # Use Dummy Backend
            dmap_file.write(
                DEVICE_ALIAS_REG
                + " (dummy?map=../include/"
                + reg_map_file
                + ")\n"
            )
        else:  # Use PCIe (xdma) Backend
            dmap_file.write(
                DEVICE_ALIAS_REG
                + " (xdma:xdma/slot"
                + str(slot)
                + "?map=./include/"
                + reg_map_file
                + ")\n"
            )
