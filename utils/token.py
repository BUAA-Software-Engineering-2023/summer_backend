import jwt
import time
from django.conf import settings


def make_token(data:dict, expire:int=30*24*3600)->str:
    """
    根据给数据生成token

    :param data: token中存储的数据
    :param expire: token过期时间
    :return: 生成的token
    """
    key = settings.SECRET_KEY
    expire_at = time.time() + expire
    payload = {
        **data,
        'exp': expire_at
    }
    return jwt.encode(payload, key)
