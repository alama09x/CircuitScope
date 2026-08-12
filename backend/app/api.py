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
    print(res)
    return(res)
    
def put_device(type: str, res_str: str):
    if res_str == "null":
        dm.selected[type] = None

    dm.selected[type] = next((o for o in dm.devices[type] if o.res_str == res_str), None)
    
@app.put("/put/{type}/{res_str}")
async def put_oscope(type: str, res_str: str):
    put_device(type, res_str)

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