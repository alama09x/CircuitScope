from pyvisa import ResourceManager

from .sinusoid import Cosine

class Oscilloscope:
    """Interface to an oscilloscope."""

    def __init__(self, res_str: str, rm: ResourceManager):
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
    
    def measure_quantity(self, qty: str, src: str) -> float:
        """
        Tells the oscilloscope to measure quantity `qty` and return it.
        
        Parameters
        ----------
        
        qty : str
            The quantity to measure
        
        src: str
            The source channel
        """
        
        # TODO: more implementations
        return float(self.device.query(f":MEAS:ITEM? {qty},{src}"))

    def measure_sinusoid(self, src: str, ref: str | None) -> Cosine:
        """
        Aggregates oscilloscope measurements into a `Cosine` object.

        Parameters
        ----------
        
        src : str
            The source channel
        
        ref : str
            The reference channel
        """
        
        freq = self.measure_quantity("FREQ", src)
        ampl = self.measure_quantity("VPP", src) * 0.5
        phi = 0
        # if ref is not None:
        #     phi = float(self.device.query(f":MEAS:ITEM? RPH,{src},{ref}"));
        # else:
        #     phi = 0
        return Cosine(ampl, freq, phi)
    
    def to_obj(self) -> dict:
        return {
            "resStr": self.res_str,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serialNumber": self.serial_number,
            "firmwareRevision": self.firmware_revision,
        }
    
    def show_error(self) -> str:
        return self.device.query(":SYST:ERR?")