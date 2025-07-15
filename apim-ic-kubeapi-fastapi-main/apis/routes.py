import setting.k8s as k8s
from schema.route import RouteItem, RouteResponse

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import httpx
import orjson

router = APIRouter(
    prefix="/kubeapi/routes"
)

@router.post(
    "/",
    tags=["Routes"],
    summary="Route 추가",
    description="Server에 적용할 Route를 생성합니다.",
    responses={
        201: {"description": "Route가 성공적으로 생성됨"},
        400: {"description": "잘못된 요청"},
        409: {"description": "이름이 동일한 Route가 이미 존재함"}
        }
)
async def create_route(data: RouteItem):
    return(
        {"route-name": data.name,
         "spec": data
        }
    )
