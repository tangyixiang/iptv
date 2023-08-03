from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Devices
from datetime import datetime
from app.config.security import check_token
import os


router = APIRouter(prefix="/adb", dependencies=[Depends(check_token)])


@router.get("/reboot")
async def reboot(deviceId: str, db: Session = Depends(getSesion)):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    os.system(f"adb connect {host}")
    os.system("adb shell")
    os.system("adb reboot")
    return {"message": "ok"}


@router.get("/install")
async def install_apk(path: str, deviceId: str, db: Session = Depends(getSesion)):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    os.system(f"adb connect {host}")
    os.system(f"adb install -r {path}")
    return {"message": "ok"}


# 连接设备
async def connect_device(deviceId: str, db: Session = Depends(getSesion)):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    os.system(f"adb connect {host}")


# 管理wifi
async def manage_wlan(operate: str, db: Session = Depends(getSesion)):
    if operate == "open":
        os.system(f"adb shell ifconfig wlan0 up")
    else:
        os.system(f"adb shell ifconfig wlan0 down")
    os.system(f"adb disconnect {host}")
    return {"message": "ok"}


# 管理有线网络
async def manage_eth(operate: str, db: Session = Depends(getSesion)):
    if operate == "open":
        os.system(f"adb shell ifconfig eth0 up")
    else:
        os.system(f"adb shell ifconfig eth0 down")
    os.system(f"adb disconnect {host}")
    return {"message": "ok"}
