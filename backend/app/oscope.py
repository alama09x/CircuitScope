from pyvisa import ResourceManager

class DeviceNotFoundError(Exception): pass

# Use native Python implementation of VISA
rm = ResourceManager("@py")

POPULAR_OSCOPE_MODELS = ["DS1", "DHO", "DSO"]


"""Searches for connected oscilloscopes."""
def find_oscopes() -> list[Oscilloscope]:
    resources = rm.list_resources()

    def is_oscope(s: str) -> bool:
        for model in POPULAR_OSCOPE_MODELS:
            if f"::{model}" in s:
                return True
        return False

    resource_strs = list(filter(is_oscope, resources))
    oscopes_tmp = list(map(Oscilloscope, resource_strs))
    oscopes = list(filter(lambda o: o.device is not None, oscopes_tmp))
    return oscopes

"""Interface to an oscilloscope."""
class Oscilloscope:
    """Note: if the device is unplugged during rm.open_resource, the oscilloscope interface will be incomplete and should be destroyed."""
    def __init__(self, res_str: str):
        self.res_str = res_str
        try:
            self.device = rm.open_resource(res_str)
        except ValueError:
            self.device = None
            return

        self.idn: str = self.device.query("*IDN?")
        [self.manufacturer, self.model, self.serial_number, self.firmware_revision] = self.idn.split(",")
    
    def __del__(self):
        self.device.close()
    
    def to_obj(self) -> dict:
        return {
            "resStr": self.res_str,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serialNumber": self.serial_number,
            "firmwareRevision": self.firmware_revision,
        }

class DeviceManager:
    def __init__(self):
        self.oscopes: list[Oscilloscope] = []
        self.selected_oscope: Oscilloscope | None = None
    
    def find_oscopes(self) -> list[str]:
        resources = rm.list_resources()

        def is_oscope(s: str) -> bool:
            for model in POPULAR_OSCOPE_MODELS:
                if f"::{model}" in s:
                    return True
            return False

        return list(filter(is_oscope, resources))
        
    
    def update_oscopes(self):
        new_strs = self.find_oscopes()

        # Edit the old list so it resembles the new list
        print(f"New_strs: {new_strs}")

        # Add new oscopes
        for new_str in new_strs:
            if next((o for o in self.oscopes if new_str == o.res_str), None) is None:
                print(f"Appended {new_str}!")
                self.oscopes.append(Oscilloscope(new_str))

        # Remove obsolete oscopes
        for oscope in self.oscopes:
            if next((ns for ns in new_strs if ns == oscope.res_str), None) is None:
                if (self.selected_oscope.res_str == oscope.res_str):
                    self.selected_oscope = None
                self.oscopes.remove(oscope)
        
        # If selected oscope was removed, but list has one elem, set it
        if (self.selected_oscope is None and len(self.oscopes) == 1):
            self.selected_oscope = self.oscopes[0]
        