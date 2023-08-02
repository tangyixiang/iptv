from fastapi import APIRouter, Depends, Query
from app.config.security import create_access_token
from pydantic import BaseModel
from app.config.db import *
from app.common import resp
from datetime import timedelta
from app.config.log import logger
from app.model.device import User_Info

router = APIRouter(prefix="/auth")


class UserInfo(BaseModel):
    username: str
    password: str


@router.post("/login", summary="用户登录认证")
async def login_access_token(user_info: UserInfo, db: Session = Depends(getSesion)):
    """
    用户登录
    :param db:
    :param user_info:
    :return:
    """

    user = db.query(User_Info).filter(User_Info.user_name == user_info.username, User_Info.password == user_info.password).one()
    if not user:
        logger.info(f"用户邮箱认证错误: email{user_info.username} password:{user_info.password}")
        return resp.fail(message="用户名或者密码错误")

    # 如果用户正确通过 则生成token
    # 设置过期时间
    access_token_expires = timedelta(minutes=60 * 12)

    # 登录token 只存放了user.id
    return resp.ok(
        data={
            "token": create_access_token(user.id, expires_delta=access_token_expires),
        }
    )
