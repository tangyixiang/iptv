from pydantic import BaseModel, Field


class config_param(BaseModel):
    deviceId: str
    password: str = Field(None)
    adb: str = Field(None)
    apk: str = Field(None)


class eth_param(BaseModel):
    deviceId: str
    open: str = Field(None)
    ip_model: str = Field(None)
    ip_address: str = Field(None)
    mask: str = Field(None)
    gateway: str = Field(None)


class wlan_param(BaseModel):
    deviceId: str
    open: str = Field(None)
    ssid: str = Field(None)
    password: str = Field(None)


class hotspot_param(BaseModel):
    deviceId: str
    open: str = Field(None)
    ssid: str = Field(None)
    password: str = Field(None)
