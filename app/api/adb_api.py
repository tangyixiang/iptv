import os, re
import hashlib
import adbutils
from binascii import hexlify
from fastapi import APIRouter, Depends, HTTPException
from app.config.db import *
from app.model.device import Devices
from app.config.security import check_token
from app.model.params import *
from adbutils import AdbTimeout


# router = APIRouter(prefix="/adb", dependencies=[Depends(check_token)])
router = APIRouter(prefix="/adb")

temp_dir = "D:\\temp"
hostapd_path = f"{temp_dir}\hostapd.conf"
wpa_supplicant_path = f"{temp_dir}\wpa_supplicant.conf"


@router.get("/reboot")
def reboot(deviceId: str, db: Session = Depends(getSesion)):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    os.system(f"adb connect {host}")
    os.system("adb shell")
    os.system("adb reboot")
    return {"message": "ok"}


@router.get("/install")
def install_apk(path: str, deviceId: str, db: Session = Depends(getSesion)):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    os.system(f"adb connect {host}")
    os.system(f"adb install -r {path}")
    return {"message": "ok"}


# 连接设备
def connect_device(deviceId: str, db: Session):
    device = db.query(Devices).filter(Devices.id == deviceId).one()
    host = device.ip_address + ":" + device.port
    # 连接
    try:
        adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        adb.connect(host, timeout=3.0)
        return host
    except AdbTimeout as e:
        raise HTTPException(status_code=400, detail="设备连接失败")


# 管理wifi
@router.post("/wifi")
def manage_wlan(param: wlan_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    if param.open == "true":
        os.system(f"adb shell ifconfig wlan0 up")
        os.system(f"adb pull /data/misc/wifi/wpa_supplicant.conf {wpa_supplicant_path}")
        with open(wpa_supplicant_path, "r") as f:
            content = f.read()
            pattern = r"network={[^}]*}"
            networks = re.findall(pattern, content, re.M)
            # print(networks)

            # 添加到内容末尾
            with open(wpa_supplicant_path, "w") as f:
                f.write(content + "\n")
                f.write("network={" + "\n")
                f.write(f'   ssid="{param.ssid}"' + "\n")
                f.write(f'   psk="{param.password}"' + "\n")
                f.write("   key_mgmt=WPA-PSK" + "\n")
                f.write("   priority=4" + "\n")
                f.write("}" + "\n")
        os.system(f"adb push {wpa_supplicant_path} /data/misc/wifi/wpa_supplicant.conf")
    else:
        os.system(f"adb shell ifconfig wlan0 down")
    os.system(f"adb disconnect {host}")
    return {"message": "ok"}


# 管理有线网络
@router.post("/eth")
def manage_eth(param: eth_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    if param.open == "true":
        os.system(f"adb shell ifconfig eth0 up")
        if param.ip_model == "manual":
            os.system("adb shell settings put global eth_mode manual")
            os.system(f"adb shell settings put global eth_ip {param.ip_address}")
            os.system(f"adb shell settings put global eth_mask {param.mask}")
            os.system(f"adb shell settings put global eth_dns1 {param.gateway}")
        else:
            os.system("adb shell settings put global eth_mode dhcp")
    else:
        os.system(f"adb shell ifconfig eth0 down")
    os.system(f"adb disconnect {host}")
    return {"message": "ok"}


@router.post("/hotspot")
def open_hotspot(param: hotspot_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    if param.open == "true":
        os.system("adb shell settings put global wifi_ap_on 1")
        os.system(f"adb pull /data/misc/wifi/hostapd.conf {hostapd_path}")
        with open(hostapd_path, "r") as f:
            # 添加到内容末尾
            lines = ["interface=wlan0", "driver=nl80211", "ctrl_interface=/data/misc/wifi/hostapd", f"ssid={param.ssid}", "channel=6", "ieee80211n=1", "hw_mode=g", "ignore_broadcast_ssid=0", "wpa=1", "wpa_pairwise=TKIP", f"wpa_psk={get_hotspot_password(param.ssid,param.password)}"]
            with open(hostapd_path, "w") as f:
                for line in lines:
                    f.write(line + "\n")
        os.system(f"adb push {hostapd_path} /data/misc/wifi/hostapd.conf")
    else:
        os.system("adb shell settings put global wifi_ap_on 0")
    os.system(f"adb disconnect {host}")
    return {"message": "ok"}


def get_hotspot_password(ssid: str, password: str):
    dk_len = 32  # 256 bits
    iterations = 4096
    # Use PBKDF2 with SSID as salt to derive the PSK
    psk = hashlib.pbkdf2_hmac("sha1", bytes(password, "utf-8"), bytes(ssid, "utf-8"), iterations, dk_len)
    # Convert derived key to hex string
    hex_psk = hexlify(psk).decode("utf-8")
    return hex_psk
