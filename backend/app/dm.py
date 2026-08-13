from pyvisa import ResourceManager

from .device import Device
from .oscope import Oscilloscope
from .fgen import FunctionGenerator
# import serial

MODEL_SELECTION: dict[str, list[str]] = {
    "oscope": ["DS1", "DHO", "DSO"],
    "fgen": ["BG03TBZL"],
}

class DeviceManager:
    def __init__(self):
        # Use native Python implementation of VISA
        self.rm = ResourceManager("@py")
        self.devices: dict[str, list[Device]] = { "oscope": [], "fgen": [] }
        self.selected: dict[str, Device] = { "oscope": None, "fgen": None }

    def find_device_strs(self, models: list[str]) -> list[str]:
        resources = self.rm.list_resources()

        print(resources)
        def is_valid_device(s: str) -> bool:
            for model in models:
                if model in s:
                    return True
            return False

        return list(filter(is_valid_device, resources))

    def update_devices(self, type: str):
        new_strs = self.find_device_strs(MODEL_SELECTION[type])

        # Add new device
        for new_str in new_strs:
            if next((d for d in self.devices[type] if new_str == d.res_str), None) is None:
                match type:
                    case "oscope": self.devices[type].append(Oscilloscope(new_str, self.rm))
                    case "fgen": self.devices[type].append(FunctionGenerator(new_str, self.rm))

        # Remove obsolete devices
        for device in self.devices[type]:
            if next((ns for ns in new_strs if ns == device.res_str), None) is None:
                if (self.selected[type].res_str == device.res_str):
                    self.selected[type] = None
                self.devices[type].remove(device)
        
        # If selected device was removed, but list has one elem, set it
        if (self.selected[type] is None and len(self.devices[type]) == 1):
            self.selected[type] = self.devices[type][0]