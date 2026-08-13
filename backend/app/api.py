from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from .device import Device
from .dm import DeviceManager
from .oscope import Oscilloscope

from .sinusoid import Cosine

dm = DeviceManager()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_devices(type: str) -> str:
    dm.update_devices(type)
    objs = list(map(Device.to_obj, dm.devices[type]))
    if dm.selected[type] is not None:
        selected = dm.devices[type].index(dm.selected[type])
    else:
        selected = -1
    
    return json.dumps({"selected": selected, f"{type}s": objs})

@app.get("/update")
def update_all_devices() -> str:
    result = {}
    for type in dm.devices.keys():
        dm.update_devices(type)
        objs = list(map(Device.to_obj, dm.devices[type]))
        if dm.selected[type] is not None:
            selected = dm.devices[type].index(dm.selected[type])
        else:
            selected = -1
        result[type] = {"selected": selected, "devices": objs}
    res = json.dumps(result)
    return(res)
    
@app.put("/put/{type}/{res_str:path}")
async def put_device(type: str, res_str: str):
    if res_str == "null":
        dm.selected[type] = None
        return

    dm.selected[type] = next((o for o in dm.devices[type] if o.res_str == res_str), None)

@app.get('/fgen/apply/{waveform}/{freq}/{ampl}/{offset}')
async def fgen_apply(waveform: str, freq: str, ampl: str, offset: str) -> str:
    dm.selected["fgen"].apply(waveform, freq, ampl, offset)
    return ""

@app.get('/fgen/apply/{waveform}/{freq}/{ampl}')
async def fgen_apply1(waveform: str, freq: str, ampl: str) -> str:
    dm.selected["fgen"].apply(waveform, freq, ampl, None)
    return ""

@app.get('/fgen/apply/{waveform}/{freq}')
async def fgen_apply2(waveform: str, freq: str) -> str:
    dm.selected["fgen"].apply(waveform, freq, None, None)
    return ""

@app.get('/fgen/pulse/{period}')
async def fgen_pulse(period: str) -> str:
    dm.selected["fgen"].res.write(f":PULS:PER {period}")
    return ""

@app.get('/fgen/apply/{waveform}')
async def fgen_apply3(waveform: str) -> str:
    dm.selected["fgen"].apply(waveform, None, None, None)
    return ""

@app.get("/get/{type}")
async def update_devices(type: str) -> str:
    return update_devices(type)

@app.get("/oscope/measure/{qty}/{src}")
async def measure(qty: str, src: str) -> str:
    oscope = dm.selected["oscope"]
    return json.dumps({ "value": oscope.measure_quantity(qty, src) })

@app.get("/oscope/sinusoid/{src}/{ref}")
async def measure_sinusoid(src: str, ref: str) -> str:
    oscope = dm.selected["oscope"]
    if oscope is None: return ""

    cos = oscope.measure_sinusoid(src, ref)
    return json.dumps(cos.to_obj())

@app.get("/oscope/sinusoid/{src}")
async def measure_sinusoid2(src: str) -> str:
    oscope = dm.selected["oscope"]
    if oscope is None: return ""
    cos = oscope.measure_sinusoid(src, None)
    return json.dumps(cos.to_obj())

@app.get("/ocsope/error")
async def get_error() -> str:
    if dm.selected["oscope"] is not None:
        return dm.selected["oscope"].show_error()
    else:
        return "No oscilloscope connected"