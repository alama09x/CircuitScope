class Cosine:
    def __init__(self, ampl: float, freq: float, phi: float):
        """
        Creates a wave of the form `ampl*cos(2pi*freq*t + phi)`

        Parameters
        ----------
        ampl : float
            The wave's amplitude
        freq : float
            The wave's frequency
        phi : float
            The wave's phase
        """
        self.amplitude = ampl
        self.frequency = freq
        self.phase = phi
    
    def to_obj(self) -> dict:
        return { "amplitude": self.amplitude, "frequency": self.frequency, "phase": self.phase }

    def __str__(self) -> str:
        return f"{self.amplitude}cos(2pi*{self.frequency}*t + {self.phase}deg)"