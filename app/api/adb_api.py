import os, re
import hashlib
import adbutils
from binascii import hexlify
from fastapi import APIRouter, Depends, HTTPException
from app.config.db import *
from app.model.device import Devices, Device_Config
from app.config.security import check_token
from app.model.operate_params import *
from adbutils import AdbTimeout
from loguru import logger


# router = APIRouter(prefix="/adb", dependencies=[Depends(check_token)])
router = APIRouter(prefix="/adb")

temp_dir = "temp"
softap_path = f"{temp_dir}/softap.conf"
wpa_supplicant_path = f"{temp_dir}/wpa_supplicant.conf"
eth_path = f"{temp_dir}/ipconfig.txt"

os.makedirs(temp_dir, exist_ok=True)


@router.get("/reboot")
def reboot(deviceId: str, db: Session = Depends(getSesion)):
    host = connect_device(deviceId, db)

    logger.info(f"准备重启设备:{host}")
    os.system("adb shell reboot")
    logger.info(f"重启设备完成:{host}")
    os.system(f"adb disconnect")
    return {"message": "ok"}


@router.post("/apk/open")
def apk_model(param: apk_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    value = 0
    if param.open == "true":
        value = 1
        os.system("adb shell settings put global install_non_market_apps 1")
    else:
        os.system("adb shell settings put global install_non_market_apps 0")

    config = db.query(Device_Config).filter(Device_Config.device_id == param.deviceId).one_or_none()
    if config:
        config.apk_install_swtich = value
    else:
        temp_config = Device_Config(device_id=param.deviceId, apk_install_swtich=value)
        db.add(temp_config)
    db.commit()
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
        logger.info(f"开始连接设备:{host}")
        adb.connect(host, timeout=3.0)
        logger.info(f"连接设备成功:{host}")
        return host
    except AdbTimeout as e:
        raise HTTPException(status_code=500, detail="设备连接失败")


# 管理wifi
@router.post("/wifi")
def manage_wlan(param: wlan_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    value = 0
    if param.open == "true":
        value = 1
        logger.info(f"开始修改设备WiFi数据,设备:{host}")
        os.system(f"adb shell settings put global wifi_on 1")
        os.system(f"adb pull /data/misc/wifi/wpa_supplicant.conf {wpa_supplicant_path}")
        with open(f"{wpa_supplicant_path}", "r") as f:
            content = f.read()
            pattern = r"network={[^}]*}"
            networks = re.findall(pattern, content, re.M)
            # print(networks)

            # 添加到内容末尾
            with open(f"{wpa_supplicant_path}", "w") as f:
                f.write(content + "\n")
                f.write("network={" + "\n")
                f.write(f'   ssid="{param.ssid}"' + "\n")
                f.write(f'   psk="{param.password}"' + "\n")
                f.write("   key_mgmt=WPA-PSK" + "\n")
                f.write("   priority=4" + "\n")
                f.write("}" + "\n")
        os.system(f"adb push {wpa_supplicant_path} /data/misc/wifi/wpa_supplicant.conf")
        logger.info(f"修改设备WiFi数据完成,设备:{host}")
    else:
        logger.info(f"关闭设备WiFi,设备:{host}")
        os.system(f"adb shell settings put global wifi 0")
    os.system(f"adb disconnect")

    config = db.query(Device_Config).filter(Device_Config.device_id == param.deviceId).one_or_none()
    if config:
        config.wlan_swtich = value
        config.wlan_ssid = param.ssid
        config.wlan_password = param.password

    else:
        temp_config = Device_Config(device_id=param.deviceId, wlan_swtich=value, wlan_ssid=param.ssid, wlan_password=param.password)
        db.add(temp_config)
    db.commit()

    return {"message": "ok"}


# 管理有线网络
@router.post("/eth")
def manage_eth(param: eth_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    value = 0
    if param.open == "true":
        value = 1
        logger.info(f"开始修改设备有线网络数据,设备:{host}")
        os.system(f"adb shell ifconfig eth0 up")
        if param.ip_model == "manual":
            logger.info(f"开始修改设备有线网络数据，修改数据库中的数据,设备:{host}")
            os.system("adb shell settings put secure eth_mode manual")
            os.system(f"adb shell settings put secure eth_ip {param.ip_address}")
            os.system(f"adb shell settings put secure eth_mask {param.mask}")
            os.system(f"adb shell settings put secure eth_dns1 {param.gateway}")
        else:
            logger.info(f"开始修改设备有线网络数据，设置获取网络模式为dhcp,设备:{host}")
            os.system("adb shell settings put secure eth_mode dhcp")
    else:
        os.system(f"adb shell ifconfig eth0 down")

    logger.info(f"准备重启设备:{host}")
    os.system(f"adb reboot {host}")
    os.system(f"adb disconnect")
    logger.info(f"开始修改数据库数据:{host}")
    device = db.query(Devices).filter(Devices.id == param.deviceId).one()
    device.ip_address = param.ip_address
    config = db.query(Device_Config).filter(Device_Config.device_id == param.deviceId).one_or_none()
    if config:
        config.eth_swtich = value
        config.eth_ip_method = param.ip_model
        config.eth_ip_address = param.ip_address
        config.eth_net_mask = param.mask
        config.eth_gateway = param.gateway
    else:
        temp_config = Device_Config(device_id=param.deviceId, eth_swtich=value, eth_ip_method=param.ip_model, eth_ip_address=param.ip_address, eth_net_mask=param.mask, eth_gateway=param.gateway)
        db.add(temp_config)
    db.commit()
    return {"message": "ok"}


# @router.post("/hotspot")
# def open_hotspot(param: hotspot_param, db: Session = Depends(getSesion)):
#     if os.path.exists(f"{softap_path}"):
#         os.remove(f"{softap_path}")
#     # 创建空白文件
#     open(f"{softap_path}", "w").close()
#     # 向文件中写入内容
#     with open(f"{softap_path}", "w") as file:
#         length = len(param.ssid)
#         content = f"0000 0001 {str(length).zfill(4)} {get_hotspot_ssid(param.ssid)} 0400 0008"
#         file.write(content + "\n")
#         if param.password:
#             pwd = get_host_pwd(param.password)
#             file.write(pwd + " ")
#     return {"message": "ok"}


@router.post("/hotspot")
def open_hotspot(param: hotspot_param, db: Session = Depends(getSesion)):
    host = connect_device(param.deviceId, db)
    value = 0
    if param.open == "true":
        value = 1
        logger.info(f"开始开启设备热点,设备:{host}")
        os.system("adb shell settings put global wifi_ap_on 1")
        logger.info(f"开始下载设备热点数据文件,设备:{host}")
        os.system(f"adb pull /data/misc/wifi/softap.conf {softap_path}")
        # 向文件中写入内容
        with open(f"{softap_path}", "w") as file:
            length = len(param.ssid)
            if param.password:
                content = f"0000 0001 {str(length).zfill(4)} {get_hotspot_ssid(param.ssid)} 0004 0000"
                pwd = get_host_pwd(param.password)
                data = content + "\r\n" + pwd
                data = bytes.fromhex(data).decode("utf-8")
                file.write(data)
            else:
                content = f"0000 0001 {str(length).zfill(4)} {get_hotspot_ssid(param.ssid)} 0000 0000"
                data = bytes.fromhex(content).decode("utf-8")
                file.write(data)
        logger.info(f"开始推送softap配置文件,设备:{host}")
        os.system(f"adb push {softap_path} /data/misc/wifi/softap.conf")
        logger.info(f"推送softap配置文件完成,设备:{host}")
    else:
        logger.info(f"关闭设备热点,设备:{host}")
        os.system("adb shell settings put global wifi_ap_on 0")
    os.system(f"adb disconnect")

    config = db.query(Device_Config).filter(Device_Config.device_id == param.deviceId).one_or_none()
    if config:
        config.hotspot_swtich = value
        config.hotspot_ssid = param.ssid
        config.hotspot_password = param.password
    else:
        temp_config = Device_Config(device_id=param.deviceId, hotspot_swtich=value, hotspot_ssid=param.ssid, hotspot_password=param.password)
        db.add(temp_config)
    db.commit()
    return {"message": "ok"}


def get_hotspot_password(ssid: str, password: str):
    dk_len = 32  # 256 bits
    iterations = 4096
    # Use PBKDF2 with SSID as salt to derive the PSK
    psk = hashlib.pbkdf2_hmac("sha1", bytes(password, "utf-8"), bytes(ssid, "utf-8"), iterations, dk_len)
    # Convert derived key to hex string
    hex_psk = hexlify(psk).decode("utf-8")
    return hex_psk


def get_hotspot_ssid(ssid: str) -> str:
    hex_string = "".join([hex(ord(c))[2:] for c in ssid])
    print(hex_string)
    groups = [hex_string[i : i + 4] for i in range(0, len(hex_string), 4)]

    # 检查最后一个组的长度
    last_group_length = len(groups[-1])

    # 如果最后一个组长度不足4，则在末尾添加"00"
    if last_group_length < 4:
        groups[-1] += "0" * (4 - last_group_length)

    result = " ".join(groups)

    if len(groups) < 3:
        result += " 0000"
    return result


def get_host_pwd(pwd: str) -> str:
    hex_string = "".join([hex(ord(c))[2:] for c in pwd])
    len_pw = hex(len(pwd))[2:]
    hex_string = len_pw.zfill(2) + hex_string
    groups = [hex_string[i : i + 4] for i in range(0, len(hex_string), 4)]
    result = " ".join(groups)
    return result
