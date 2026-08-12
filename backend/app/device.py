from pyvisa import ResourceManager

class Device:
    def __init__(self, res_str: str, rm: ResourceManager):
        self.res_str = res_str
        try:
            self.res = rm.open_resource(res_str)
        except ValueError:
            self.res = None
            return

        self.idn: str = self.res.query("*IDN?")
        [self.manufacturer, self.model, self.serial_number, self.firmware_revision] = self.idn.split(",")

    def to_obj(self) -> dict:
        return {
            "resStr": self.res_str,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serialNumber": self.serial_number,
            "firmwareRevision": self.firmware_revision,
        }
    
    def __del__(self):
        self.res.close()