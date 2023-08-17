from fastapi import APIRouter, Depends, Query
from app.config.security import create_access_token
from pydantic import BaseModel, Field
from app.config.db import *
from app.common import resp
from datetime import timedelta
from app.config.log import logger
from app.model.device import User_Info
from typing import Any, Union
from app.config.security import check_token
from app.utils.IdUtil import get_id
from datetime import datetime


router = APIRouter(prefix="/auth")


class UserInfo(BaseModel):
    username: str
    password: str


class UserParam(BaseModel):
    id: str = Field(None)
    username: str
    password: str
    name: str


@router.post("/login", summary="用户登录认证")
async def login_access_token(user_info: UserInfo, db: Session = Depends(getSesion)):
    """
    用户登录
    :param db:
    :param user_info:
    :return:
    """

    user = db.query(User_Info).filter(User_Info.user_name == user_info.username, User_Info.password == user_info.password).all()
    if not user:
        logger.info(f"{User_Info.user_name}登录失败")
        return resp.fail2(message="用户名或者密码错误")

    # 如果用户正确通过 则生成token
    # 设置过期时间
    access_token_expires = timedelta(minutes=60 * 12)

    # 登录token 只存放了user.id
    return resp.ok(
        data={
            "token": create_access_token(user[0].id, expires_delta=access_token_expires),
        }
    )


@router.get("/userInfo")
async def get_user_info(tokenInfo: Union[str, Any] = Depends(check_token), db: Session = Depends(getSesion)):
    data = db.query(User_Info).filter(User_Info.id == tokenInfo["user_id"]).one()
    data.password = ""
    return resp.ok(data=data)


@router.get("/user/add")
async def add_user(user_info: UserParam, tokenInfo: Union[str, Any] = Depends(check_token), db: Session = Depends(getSesion)):
    db_user = db.query(User_Info).filter(User_Info.name == user_info.username).one_or_none()
    if db_user:
        return resp.fail2(message="该用户名已经存在")
    user = User_Info(user_name=user_info.username, password=user_info.password)
    user.id = get_id()
    user.name = user_info.name
    user.create_time = datetime.now()
    db.add(user)
    return {"message": "ok"}


@router.get("/user/update")
async def update_user(user_info: UserParam, tokenInfo: Union[str, Any] = Depends(check_token), db: Session = Depends(getSesion)):
    db_user = db.query(User_Info).filter(User_Info.id == user_info.id).one_or_none()
    if not db_user:
        return resp.fail2(message="用户不存在")
    db_user.name = user_info.name
    db_user.password = user_info.password
    db_user.user_name = user_info.username
    db_user.update_time = datetime.now()
    db.commit()
    return {"message": "ok"}
