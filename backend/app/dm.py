from pyvisa import ResourceManager

from .oscope import Oscilloscope

POPULAR_OSCOPE_MODELS = ["DS1", "DHO", "DSO"]

class DeviceManager:
    def __init__(self):
        # Use native Python implementation of VISA
        self.rm = ResourceManager("@py")
        self.oscopes: list[Oscilloscope] = []
        self.selected_oscope: Oscilloscope | None = None
    
    def find_oscope_strs(self) -> list[str]:
        resources = self.rm.list_resources()

        def is_oscope(s: str) -> bool:
            for model in POPULAR_OSCOPE_MODELS:
                if f"::{model}" in s:
                    return True
            return False

        return list(filter(is_oscope, resources))
        
    
    def update_oscopes(self):
        new_strs = self.find_oscope_strs()

        # Add new oscopes
        for new_str in new_strs:
            if next((o for o in self.oscopes if new_str == o.res_str), None) is None:
                self.oscopes.append(Oscilloscope(new_str, self.rm))

        # Remove obsolete oscopes
        for oscope in self.oscopes:
            if next((ns for ns in new_strs if ns == oscope.res_str), None) is None:
                if (self.selected_oscope.res_str == oscope.res_str):
                    self.selected_oscope = None
                self.oscopes.remove(oscope)
        
        # If selected oscope was removed, but list has one elem, set it
        if (self.selected_oscope is None and len(self.oscopes) == 1):
            self.selected_oscope = self.oscopes[0]
