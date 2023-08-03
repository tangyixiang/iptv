from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Iptv_Plan
from app.param.device_param import Iptv_Plan_Param
from app.utils.IdUtil import get_id
from datetime import datetime
from app.config.security import check_token

router = APIRouter(prefix="/iptv", dependencies=[Depends(check_token)])


@router.get("/list")
async def list(pageSize: int, current: int, name: str = Query(None), db: Session = Depends(getSesion)):
    offset = (current - 1) * pageSize
    query_list = []
    if name:
        query_list = query_list.append(Iptv_Plan.name == name)
    data = db.query(Iptv_Plan).filter(*query_list).order_by(Iptv_Plan.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Iptv_Plan).filter(*query_list).order_by(Iptv_Plan.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.post("/add")
async def add(data: Iptv_Plan_Param, db: Session = Depends(getSesion)):
    if data.id:
        iptv_Plan = db.query(Iptv_Plan).filter(Iptv_Plan.id == data.id).first()
        iptv_Plan.name = data.name
        iptv_Plan.update_time = datetime.now()
    else:
        iptv = Iptv_Plan(**data.model_dump())
        iptv.id = get_id()
        db.add(iptv)
    db.commit()
    return {"message": "ok"}


@router.post("/del")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Iptv_Plan).filter(Iptv_Plan.id == id).delete()
    db.commit()
    return {"message": "ok"}
