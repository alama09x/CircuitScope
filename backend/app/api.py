from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from .oscope import DeviceManager, find_oscopes, Oscilloscope


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
    if dm.selected_oscope is None:
        selected = -1
    else:
        selected = dm.oscopes.index(dm.selected_oscope)
    return json.dumps({"selected": selected, "oscopes": objs})

@app.get("/measure/{quantity}/{source}")
async def measure(quantity: str, source: str):
    value = float(dm.selected_oscope.device.query_ascii_values(f":MEAS:ITEM? {quantity},{source}")[0])
    return value

@app.put("/put-oscope/{res_str}")
async def put_oscope(res_str: str):
    if res_str == "null":
        dm.selected_oscope = None

    dm.selected_oscope = next((o for o in dm.oscopes if o.res_str == res_str), None)

    # Debug
    if (dm.selected_oscope is not None):
        print(dm.selected_oscope.idn)