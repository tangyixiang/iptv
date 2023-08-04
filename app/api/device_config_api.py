from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Device_Config
from app.param.device_param import Device_Config_Param
from app.utils.IdUtil import get_id
from datetime import datetime
from app.config.security import check_token

router = APIRouter(prefix="/device_config", dependencies=[Depends(check_token)])


@router.get("/list")
async def list(pageSize: int, current: int, location_id: str = Query(None), room_id: str = Query(None), db: Session = Depends(getSesion)):
    offset = (current - 1) * pageSize
    query_list = []
    if location_id:
        query_list = query_list.append(Device_Config.location_id == location_id)
    if room_id:
        query_list = query_list.append(Device_Config.room_id == room_id)
    data = db.query(Device_Config).filter(*query_list).order_by(Device_Config.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Device_Config).filter(*query_list).order_by(Device_Config.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.get("/info")
async def get_config(id: str, db: Session = Depends(getSesion)):
    data = db.query(Device_Config).filter(Device_Config.device_id == id).all()
    if data:
        return {"data": data[0]}
    else:
        return {"data": {}}


@router.post("/add")
async def add(data: Device_Config_Param, db: Session = Depends(getSesion)):
    if data.id:
        config = db.query(Device_Config).filter(Device_Config.id == data.id).first()
        dict_data = data.model_dump()
        # 更新对象的属性
        for key, value in dict_data.items():
            setattr(config, key, value)
        config.update_time = datetime.now()
    else:
        config = Device_Config(**data.model_dump())
        config.id = get_id()
        db.add(config)
    db.commit()
    return {"message": "ok"}


@router.post("/del")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Device_Config).filter(Device_Config.id == id).delete()
    db.commit()
    return {"message": "ok"}
