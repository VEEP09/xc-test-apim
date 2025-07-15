import setting.k8s as k8s
from schema.cert import CertificateItem, CertificateResponse

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import httpx
import orjson
import base64

router = APIRouter(
    prefix="/kubeapi/certs"
)

@router.post(
    '/',
    response_model=CertificateResponse,
    tags=["Certs"],
    summary="Cert 생성",
    description="지정된 네임스페이스에 TLS 인증서 Secret을 생성합니다.",
    responses={
        200: {"description": "TLS Secret이 성공적으로 생성됨"},
        400: {"description": "잘못된 요청"},
        409: {"description": "이미 존재하는 Secret입니다"},
        500: {"description": "서버 내부 오류"}
    }
)
async def create_tls_secret(cert_item: CertificateItem):
    # Validate input
    if not all([cert_item.namespace, cert_item.name, cert_item.tls_crt, cert_item.tls_key]):
        raise HTTPException(status_code=400, detail="Invalid certificate details")

    # Prepare secret payload
    secret_payload = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": f"{cert_item.name}-cert",
            "namespace": cert_item.namespace
        },
        "type": "kubernetes.io/tls",
        "data": {
            "tls.crt": base64.b64encode(cert_item.tls_crt.encode()).decode(),
            "tls.key": base64.b64encode(cert_item.tls_key.encode()).decode()
        }
    }

    # Create secret in Kubernetes
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{cert_item.namespace}/secrets",
                headers=k8s.API_HEADER,
                json=secret_payload
            )
            
            # Check response status
            if response.status_code not in [200, 201]:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return CertificateResponse(
                data=[{
                    "name": cert_item.name,
                    "namespace": cert_item.namespace,
                    "status": "Created"
                }]
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get(
    '/',
    response_model=CertificateResponse,
    tags=["Certs"],
    summary="모든 namespace의 Cert 조회",
    description="K8S 클러스터의 모든 TLS Secrets를 불러옵니다.",
    responses={
        200: {"description": "TLS Secrets가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_namespace_tls_secrets():
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL_TLS_SECRET,
            headers=k8s.API_HEADER,
        )
        
        response_json = orjson.loads(response.text)
        
        # Filter only TLS type secrets
        tls_secrets = [
            {
                "name": item.get("metadata", {}).get("name", ""),
                "namespace": item.get("metadata", {}).get("namespace", ""),
                "uid" : item.get("metadata", {}).get("uid", ""),
                "type": item.get("type", "")
            }
            for item in response_json.get("items", [])
            if item.get("type") == "kubernetes.io/tls"
        ]
            
    return CertificateResponse(data=tls_secrets)

@router.get(
    '/{namespace}',
    response_model=CertificateResponse,
    tags=["Certs"],
    summary="특정 namespace의 Cert 조회",
    description="K8S 클러스터의 지정한 namespace의 TLS Secrets를 불러옵니다.",
    responses={
        200: {"description": "TLS Secrets가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_namespace_tls_secrets(namespace: str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/secrets",
            headers=k8s.API_HEADER,
        )
        
        response_json = orjson.loads(response.text)
        
        # Filter only TLS type secrets
        tls_secrets = [
            {
                "name": item.get("metadata", {}).get("name", ""),
                "namespace": item.get("metadata", {}).get("namespace", ""),
                "uid" : item.get("metadata", {}).get("uid", ""),
                "type": item.get("type", "")
            }
            for item in response_json.get("items", [])
            if item.get("type") == "kubernetes.io/tls"
        ]
            
    return CertificateResponse(data=tls_secrets)

@router.delete(
    "/",
    tags=["Certs"],
    summary="Cert 삭제",
    description="K8S 클러스터의 지정한 TLS Secret을 삭제합니다.",
    responses={
        200: {"description": "Cert가 성공적으로 삭제됨"},
        404: {"description": "Cert를 찾을 수 없음"},
        400: {"description": "잘못된 요청"}
    }
)
async def delete_cert(name: str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL_TLS_SECRET,
            headers=k8s.API_HEADER
        )
        response_json = response.json()
        
        found_cert = next(
            (item for item in response_json.get("items", []) 
             if item["metadata"]["name"] == name or item["metadata"]["name"] == f"{name}-cert"),
            None
        )

        if not found_cert:
            raise HTTPException(
                status_code=404, 
                detail=f"TLS-Secret with name {name} not found"
            )

        # 찾은 Cert의 namespace 추출
        cert_name = found_cert["metadata"]["name"]
        namespace = found_cert["metadata"]["namespace"]

        delete_response = await client.delete(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/secrets/{cert_name}",
            headers=k8s.API_HEADER
        )
        
        if delete_response.status_code != 200:
            raise HTTPException(
                status_code=delete_response.status_code,
                detail=f"Error: {delete_response.text}"
            )

        return JSONResponse(
            status_code=delete_response.status_code,
            content={
                "message": f"{namespace} 네임스페이스의 {name} TLS-Secret이 성공적으로 삭제됨"
            }
        )