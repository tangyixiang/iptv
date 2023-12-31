from fastapi import APIRouter, Depends, Query
from app.config.db import *
from app.model.device import Location
from app.param.device_param import Location_Param
from app.utils.IdUtil import get_id
from datetime import datetime
from app.config.security import check_token

router = APIRouter(prefix="/location", dependencies=[Depends(check_token)])


@router.get("/all")
async def list(db: Session = Depends(getSesion)):
    data = db.query(Location).all()
    return {"data": data}


@router.get("/list")
async def list(pageSize: int, current: int, name: str = Query(None), db: Session = Depends(getSesion)):
    offset = (current - 1) * pageSize
    query_list = []
    if name:
        query_list = query_list.append(Location.name == name)
    data = db.query(Location).filter(*query_list).order_by(Location.create_time.desc()).offset(offset).limit(pageSize).all()
    total = db.query(Location).filter(*query_list).order_by(Location.create_time.desc()).offset(offset).limit(pageSize).count()
    return {"total": total, "list": data}


@router.post("/add")
async def add(data: Location_Param, db: Session = Depends(getSesion)):
    if data.id:
        location = db.query(Location).filter(Location.id == data.id).first()
        location.name = data.name
        location.update_time = datetime.now()
    else:
        location = Location(**data.model_dump())
        location.id = get_id()
        db.add(location)
    db.commit()
    return {"message": "ok"}


@router.delete("/del/{id}")
async def delete(id: str, db: Session = Depends(getSesion)):
    db.query(Location).filter(Location.id == id).delete()
    db.commit()
    return {"message": "ok"}
