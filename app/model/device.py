from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER, DATETIME
from app.config.db import engine
from datetime import datetime


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Location(Base):
    __tablename__ = "location"

    id = Column(VARCHAR(32), primary_key=True, comment="id")
    name = Column(VARCHAR(32), comment="名称")
    create_time = Column(DATETIME, default=datetime.now(), comment="创建时间")
    update_time = Column(DATETIME, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")


class Rom_Info(Base):
    __tablename__ = "rom_info"

    id = Column(VARCHAR(32), primary_key=True)
    name = Column(VARCHAR(32), comment="名称")
    create_time = Column(DATETIME, default=datetime.now(), comment="创建时间")
    update_time = Column(DATETIME, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")


class Iptv_Plan(Base):
    __tablename__ = "iptv_plan"

    id = Column(VARCHAR(32), primary_key=True)
    name = Column(VARCHAR(32), comment="名称")
    create_time = Column(DATETIME, default=datetime.now(), comment="创建时间")
    update_time = Column(DATETIME, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")


class Devices(Base):
    __tablename__ = "devices"

    id = Column(VARCHAR(32), primary_key=True)
    location_id = Column(VARCHAR(32), comment="安装实体")
    room_id = Column(VARCHAR(32), comment="房间号")
    rom_version = Column(VARCHAR(32), comment="rom版本")
    iptv_network_plan = Column(VARCHAR(255), comment="iptv方案")
    mac_address = Column(VARCHAR(255), comment="mac地址")
    ip_address = Column(VARCHAR(64), comment="ip地址")
    port = Column(VARCHAR(8), comment="端口号")
    other_info = Column(TEXT, comment="其他信息")
    image_url = Column(VARCHAR(255), comment="图片地址")
    create_time = Column(DATETIME, default=datetime.now(), comment="创建时间")
    update_time = Column(DATETIME, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")


class Device_Config(Base):
    __tablename__ = "device_config"

    device_id = Column(VARCHAR(32), primary_key=True, comment="设备ID")
    password = Column(VARCHAR(32), comment="管理密码")
    apk_install_swtich = Column(INTEGER(1), comment="apk远程安装")
    adb_swtich = Column(INTEGER(1), comment="adb开关 0 关闭 1 开启")

    eth_swtich = Column(INTEGER(1), comment="有线开启 0 关闭 1 开启")
    eth_ip_method = Column(VARCHAR(4), comment="有线ip获取模式")
    eth_ip_address = Column(VARCHAR(64), comment="有线ip地址")
    eth_net_mask = Column(VARCHAR(64), comment="子网掩码")
    eth_gateway = Column(VARCHAR(64), comment="网关")

    wlan_swtich = Column(INTEGER(1), comment="wifi开关 0 关闭 1 开启")
    wlan_ssid = Column(VARCHAR(32), comment="wifi ssid名称")
    wlan_encrypt_mode = Column(VARCHAR(64), comment="wifi加密模式")
    wlan_password = Column(VARCHAR(64), comment="wifi ssid名称")

    hotspot_swtich = Column(INTEGER(1), comment="热点开关 0 关闭 1 开启")
    hotspot_password = Column(VARCHAR(32), comment="热点密码")

    create_time = Column(DATETIME, default=datetime.now(), comment="创建时间")
    update_time = Column(DATETIME, default=datetime.now(), onupdate=datetime.now(), comment="更新时间")


Base.metadata.create_all(engine)
