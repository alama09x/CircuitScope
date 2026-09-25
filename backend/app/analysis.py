import numpy as np
from numpy import ndarray
import asyncio
from matplotlib import pyplot as plt

from .dm import DeviceManager
from .fgen import FunctionGenerator
from .oscope import Oscilloscope
from .model import fit_to_model

INITIAL_SCALE = 5.0E-4
FLAT_THRESHOLD = 0.5
DATA_POINTS = 1000

class CircuitAnalysis:
    def __init__(self, v_data: ndarray, t_data: ndarray, sampling_period: float):
        self.v_data = v_data
        self.t_data = t_data
        self.sampling_period = sampling_period

    @classmethod
    async def create(cls, dm: DeviceManager) -> CircuitAnalysis:
        fgen: FunctionGenerator = dm.selected["fgen"]
        oscope: Oscilloscope = dm.selected["oscope"]

        fgen.res.write(":APPL:SQU 100, 10")

        # Configure channels
        for i in [1, 2]:
            oscope.res.write(f":CHAN{i}:COUP DC")
            oscope.res.write(f":CHAN{i}:OFFS 0")
            oscope.res.write(f":CHAN{i}:DISP ON")
            oscope.res.write(f":CHAN{i}:PROB 1")
            oscope.res.write(f":CHAN{i}:SCAL 10")
            oscope.res.write(f":CHAN{i}:UNIT VOLT")
            oscope.res.write(f":CHAN{i}:POS 0")
        
        # Configure trigger
        oscope.res.write(":TRIG:SWE SING")
        oscope.res.write(":TRIG:EDGE:SOUR CHAN1")
        oscope.res.write(":TRIG:EDGE:LEVEL 0")
        oscope.res.write(":TRIG:EDGE:SLOP POS")

        # Configure time frame
        oscope.res.write(":TIM:HREF:MODE LB")
        oscope.res.write(":TIM:HREF:POS -500")
        oscope.res.write(":TIM:DEL:ENAB 0")

        # Configure data query
        oscope.res.write(":WAV:SOUR CHAN2")
        oscope.res.write(":WAV:MODE NORM")
        oscope.res.write(":WAV:FORM ASCII")
        oscope.res.write(":WAV:POIN 100")

        _ = await CircuitAnalysis.auto_scale(oscope)
        oscope.res.write(":SING")

        oscope.res.write(":WAV:STAR 1")
        oscope.res.write(f":WAV:POIN {DATA_POINTS}")

        sampling_period = float(oscope.res.query(":WAV:XINC?"))
        data0: list[float] = oscope.res.query_ascii_values(":WAV:DATA?", separator=separator)

        v_data = np.array(data0)
        t_data = np.linspace(0, sampling_period * DATA_POINTS, DATA_POINTS)

        if (fit := fit_to_model(v_data, t_data)):
            print(f"Model: {fit["model"].name}")
            print(f"Estimated parameters: {fit["popt"]}")
            print(f"Average error: {fit["avgerr"]}")

            plt.plot(t_data, v_data)
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (V)")
            plt.plot(t_data, fit["model"].fn(t_data, *fit["popt"]))
            plt.grid(True)

            plt.show()
        else:
            print("Fit no model")


        return cls(v_data=v_data, t_data=t_data, sampling_period=sampling_period)
    
    async def auto_scale(oscope: Oscilloscope) -> float:
        scale = INITIAL_SCALE
        i = 0
        while True:
            oscope.res.write(f":TIM:SCAL {scale}")
            oscope.res.write(f":TIM {5 * scale}")

            if (i % 10 == 0):
                oscope.res.write(":SING")
            else:
                oscope.res.write(":TFOR")

            # Wait for trigger
            while True:
                await asyncio.sleep(0.0001)
                status: str = oscope.res.query(":TRIG:STAT?").strip()
                if status == "STOP":
                    break


            oscope.res.write(":WAV:STAR 700")
            oscope.res.write(":WAV:STOP 800")
            data0: list[float] = oscope.res.query_ascii_values(":WAV:DATA?", separator=separator)

            data = np.array(data0)
            max_diff = data.max() - data.min()

            if max_diff > FLAT_THRESHOLD:
                return scale

            scale *= 0.8
            i += 1
    
    def to_json(self) -> dict:
        return {
            "vData": self.v_data.tolist(),
            "tData": self.t_data.tolist(),
            "samplingPeriod": self.sampling_period
        }


def separator(s: str) -> list[str]:
    lines = s.splitlines()
    res = list()
    for line in lines:
        res.extend(filter(lambda s: s != "", line.split(",")))
    return res