from .device import Device

class FunctionGenerator(Device):
    def apply(self, waveform: str, freq: str | None, ampl: str | None, offset: str | None):
        self.res.write(f":APPL:{waveform} " + ', '.join(list(filter(lambda s: s is not None, [freq, ampl, offset]))))