from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Rom_Info
from app.param.device_param import Rom_Info_Param
from app.utils.IdUtil import get_id
from datetime import datetime
from app.config.security import check_token

router = APIRouter(prefix="/rom", dependencies=[Depends(check_token)])


@router.get("/list")
async def list(pageSize: int, current: int, name: str = Query(None), db: Session = Depends(getSesion)):
    offset = (current - 1) * pageSize
    query_list = []
    if name:
        query_list = query_list.append(Rom_Info.name == name)
    data = db.query(Rom_Info).filter(*query_list).order_by(Rom_Info.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Rom_Info).filter(*query_list).order_by(Rom_Info.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.post("/add")
async def add(data: Rom_Info_Param, db: Session = Depends(getSesion)):
    if data.id:
        rom_Info = db.query(Rom_Info).filter(Rom_Info.id == data.id).first()
        rom_Info.name = data.name
        rom_Info.update_time = datetime.now()
    else:
        rom = Rom_Info(**data.model_dump())
        rom.id = get_id()
        db.add(rom)
    db.commit()
    return {"message": "ok"}


@router.post("/del")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Rom_Info).filter(Rom_Info.id == id).delete()
    db.commit()
    return {"message": "ok"}
