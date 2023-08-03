from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Devices
from app.param.device_param import Devices_Param
from app.utils.IdUtil import get_id
from datetime import datetime
from app.config.security import check_token

router = APIRouter(prefix="/device", dependencies=[Depends(check_token)])


@router.get("/list")
async def list(pageSize: int, current: int, location_id: str = Query(None), room_id: str = Query(None), db: Session = Depends(getSesion)):
    offset = (current - 1) * pageSize
    query_list = []
    if location_id:
        query_list = query_list.append(Devices.location_id == location_id)
    if room_id:
        query_list = query_list.append(Devices.room_id == room_id)
    data = db.query(Devices).filter(*query_list).order_by(Devices.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Devices).filter(*query_list).order_by(Devices.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.post("/add")
async def add(data: Devices_Param, db: Session = Depends(getSesion)):
    if data.id:
        devices = db.query(Devices).filter(Devices.id == data.id).first()
        dict_data = data.model_dump()
        # 更新对象的属性
        for key, value in dict_data.items():
            setattr(devices, key, value)
        devices.update_time = datetime.now()
    else:
        devices = Devices(**data.model_dump())
        devices.id = get_id()
        db.add(devices)
    db.commit()
    return {"message": "ok"}


@router.post("/del")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Devices).filter(Devices.id == id).delete()
    db.commit()
    return {"message": "ok"}
