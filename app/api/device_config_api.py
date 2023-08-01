from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Device_Config
from app.param.device_param import Device_Config_Param
from app.utils.IdUtil import get_id
from datetime import datetime

router = APIRouter(prefix="/device_config")


@router.get("/list")
async def list(pageSize: int, pageNum: int, location_id: str = Query(None), room_id: str = Query(None), db: Session = Depends(getSesion)):
    offset = (pageNum - 1) * pageSize
    query_list = []
    if location_id:
        query_list = query_list.append(Device_Config.location_id == location_id)
    if room_id:
        query_list = query_list.append(Device_Config.room_id == room_id)
    data = db.query(Device_Config).filter(*query_list).order_by(Device_Config.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Device_Config).filter(*query_list).order_by(Device_Config.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.post("/add")
async def add(data: Device_Config_Param, db: Session = Depends(getSesion)):
    if data.id:
        Device_Config = db.query(Device_Config).filter(Device_Config.id == data.id).first()
        dict_data = data.model_dump()
        # 更新对象的属性
        for key, value in dict_data.items():
            setattr(Device_Config, key, value)
        Device_Config.update_time = datetime.now()    
    else:
        Device_Config = Device_Config(**data.model_dump())
        Device_Config.id = get_id()
        db.add(Device_Config)
    db.commit()
    return {"message": "ok"}


@router.post("/del")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Device_Config).filter(Device_Config.id == id).delete()
    db.commit()
    return {"message": "ok"}
