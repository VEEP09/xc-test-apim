import setting.k8s as k8s
from schema.ip import Deny

from fastapi import APIRouter
from fastapi.responses import JSONResponse

import httpx



router = APIRouter(
    prefix="/kubeapi/oidc"
)

@router.get(
    '/',
    tags=["Oidc"],
    summary="IP Deny 정책 전체 조회",
    description="NGINX Ingress Controller의 Oidc 정책을 불러옵니다.",
    responses={
        200: {"description": "IP Deny 정책이 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_ip_deny():
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL+'?labelSelector=type=ip',
            headers=k8s.API_HEADER, 
            )
    return JSONResponse(
        status_code=response.status_code,
        content={response.text}
    )
    # return k8s.api_url+'?labelSelector=type=ip'
