from pydantic import BaseModel, Field
from typing import Optional, List


class Location_Param(BaseModel):
    id: str = Field(None)
    name: str


class Rom_Info_Param(BaseModel):
    id: str = Field(None)
    name: str


class Iptv_Plan_Param(BaseModel):
    id: str = Field(None)
    name: str


class Devices_Param(BaseModel):
    id: str = Field(None)
    location_id: str
    room_id: str
    rom_version: str
    iptv_network_plan: str
    mac_address: str
    ip_address: str
    port: str
    other_info: str = Field(None)
    image_url: str = Field(None)


class Device_Config_Param(BaseModel):
    device_id: str = Field(None)
    password: str
    apk_install_swtich: int
    adb_swtich: int

    eth_swtich: int
    eth_ip_method: str
    eth_ip_address: str
    eth_net_mask: str
    eth_gateway: str

    wlan_swtich: str
    wlan_ssid: str
    wlan_encrypt_mode: str
    wlan_password: str

    hotspot_swtich: int
    hotspot_password: int
