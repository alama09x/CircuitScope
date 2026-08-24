from .device import Device
from .sinusoid import Cosine

class Oscilloscope(Device):
    """Interface to an oscilloscope."""
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
        return float(self.res.query(f":MEAS:ITEM? {qty},{src}"))

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
        #     phi = float(self.res.query(f":MEAS:ITEM? RPH,{src},{ref}"));
        # else:
        #     phi = 0
        return Cosine(ampl, freq, phi)
    
    def show_error(self) -> str:
        return self.res.query(":SYST:ERR?")