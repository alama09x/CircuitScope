from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from .sinusoid import Cosine
from .dm import DeviceManager, Oscilloscope

dm = DeviceManager()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/oscopes")
async def get_oscopes() -> str:
    dm.update_oscopes()
    objs = list(map(Oscilloscope.to_obj, dm.oscopes))
    if dm.selected_oscope is not None:
        selected = dm.oscopes.index(dm.selected_oscope)
    else:
        selected = -1
    
    return json.dumps({"selected": selected, "oscopes": objs})

@app.get("/measure/{qty}/{src}")
async def measure(qty: str, src: str) -> str:
    return json.dumps({ "value": dm.selected_oscope.measure_quantity(qty, src) })

@app.get("/sinusoid/{src}/{ref}")
async def measure_sinusoid(src: str, ref: str) -> str:
    if dm.selected_oscope is None: return ""
    cos = dm.selected_oscope.measure_sinusoid(src, ref)
    return json.dumps(cos.to_obj())

@app.get("/sinusoid/{src}")
async def measure_sinusoid2(src: str) -> str:
    if dm.selected_oscope is None: return ""
    cos = dm.selected_oscope.measure_sinusoid(src, None)
    return json.dumps(cos.to_obj())

@app.put("/put-oscope/{res_str}")
async def put_oscope(res_str: str):
    if res_str == "null":
        dm.selected_oscope = None

    dm.selected_oscope = next((o for o in dm.oscopes if o.res_str == res_str), None)

@app.get("/error")
async def get_error() -> str:
    if dm.selected_oscope is not None:
        return dm.selected_oscope.show_error()
    else:
        return "No oscilloscope connected"