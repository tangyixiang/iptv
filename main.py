from typing import Union
from fastapi import FastAPI, APIRouter, Depends
from app.config.db import *
from app.api.iptv_plan_api import router as iptv_router
from app.api.location_api import router as location_router
from app.api.rom_api import router as rom_router
from app.api.device_api import router as device_router
from app.api.device_config_api import router as device_config_router
from app.api.login import router as login_router


app = FastAPI()
app.include_router(location_router)
app.include_router(iptv_router)
app.include_router(rom_router)
app.include_router(device_router)
app.include_router(device_config_router)
app.include_router(login_router)
