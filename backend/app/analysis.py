import scipy
import numpy as np
from numpy import ndarray
import asyncio

from .dm import DeviceManager
from .fgen import FunctionGenerator
from .oscope import Oscilloscope

INITIAL_SCALE = 5.0E-4
FLAT_THRESHOLD = 0.5

class CircuitAnalysis:
    def __init__(self, data: ndarray, sampling_period: float):
        self.data = data
        self.sampling_period = sampling_period

    @classmethod
    async def create(cls, dm: DeviceManager):
        analysis = {}

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

        oscope.res.write(":WAV:STAR 1")
        oscope.res.write(":WAV:POIN 1000")

        sampling_period = float(oscope.res.query(":WAV:XINC?"))
        data0: list[float] = oscope.res.query_ascii_values(":WAV:DATA?", separator=separator)
        data = np.array(data0)

        return cls(data=data, sampling_period=sampling_period)
    
    async def auto_scale(oscope: Oscilloscope) -> float:
        scale = INITIAL_SCALE
        while True:
            oscope.res.write(f":TIM:SCAL {scale}")
            oscope.res.write(f":TIM {5 * scale}")

            oscope.res.write(":SING")

            # Wait for trigger
            while True:
                await asyncio.sleep(0.001)
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

            scale *= 0.9
    
    def to_json(self) -> dict:
        return {
            "data": self.data.tolist(),
            "samplingPeriod": self.sampling_period
        }

    # @classmethod
    # async def create(cls, dm: DeviceManager):
    #     analysis = {}

    #     fgen: FunctionGenerator = dm.selected["fgen"]
    #     oscope: Oscilloscope = dm.selected["oscope"]

    #     fgen.res.write(":APPL:SQU 1.0E2, 1.0E1")
    #     await asyncio.sleep(0.5)

    #     topology = "RC"
    #     filter = "low"

    #     V_f = float(oscope.res.query(":MEAS:ITEM? VTOP, CHAN1"))
    #     V_i = float(oscope.res.query(":MEAS:ITEM? VBAS, CHAN1"))
    #     oscope.res.write(":MEAS:CLE ALL")

    #     oscope.res.write(":MEAS:THR:SOUR CHAN2")
    #     oscope.res.write(":MEAS:THR:TYPE PERC")

    #     if topology == "RC":

    #         if filter == "low":
    #             rc = CircuitAnalysis.measure_rtime(oscope)
    #         elif filter == "high":
    #             rc = CircuitAnalysis.measure_ftime(oscope)

    #         oscope.res.write(":MEAS:CLE ALL")

    #         analysis["RC"] = rc

    #     elif topology == "RLC":

    #         damping = "under"

    #         overshoot = CircuitAnalysis.measure_overshoot(oscope)
    #         analysis["damping"] = damping

    #     analysis |= {
    #         "topology": topology,
    #         "filter": filter,
    #         "V_f": V_f,
    #         "V_i": V_i,
    #     }
    #     return cls(analysis)
    
    def measure_rtime(oscope: Oscilloscope) -> float:
        oscope.res.write(":MEAS:SET:MAX 63")
        oscope.res.write(":MEAS:SET:MIN 0")
        return float(oscope.res.query(":MEAS:ITEM? RTIM"))

    def measure_ftime(oscope: Oscilloscope) -> float:
        oscope.res.write(":MEAS:SET:MAX 100")
        oscope.res.write(":MEAS:SET:MIN 37")
        return float(oscope.res.query(":MEAS:ITEM? FTIM"))
    
    def measure_overshoot(oscope: Oscilloscope) -> float:
        return float(oscope.res.write(":MEAS:ITEM? OVER"))


def separator(s: str) -> list[str]:
    lines = s.splitlines()
    res = list()
    for line in lines:
        res.extend(filter(lambda s: s != "", line.split(",")))
    return res