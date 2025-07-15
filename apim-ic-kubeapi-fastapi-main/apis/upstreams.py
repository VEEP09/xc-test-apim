import setting.k8s as k8s
from schema.upstream import UpstreamItem, UpstreamResponse, UpstreamCreateRequest, UpstreamUpdateRequest

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import httpx
import orjson

router = APIRouter(
    prefix="/kubeapi/upstreams"
)

@router.get(
    '/',
    response_model=UpstreamResponse,
    tags=["Upstreams"],
    summary="Upstreams 전체 조회",
    description="K8S 클러스터의 Service를 불러옵니다.",
    responses={
        200: {"description": "Upstreams가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_upstreams():
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL_SERVICE,
            headers=k8s.API_HEADER, 
        )
        response_json = orjson.loads(response.text)
        
        items_data = [
            UpstreamItem(
                uid=item.get("metadata", {}).get("uid", ""),
                name=item.get("metadata", {}).get("name", ""),
                namespace=item.get("metadata", {}).get("namespace", ""),
                ports=[port.get("port", 0) for port in item.get("spec", {}).get("ports", [])]
            )
            for item in response_json.get("items", [])
        ]
          
            
    return UpstreamResponse(data=items_data)

@router.get(
    '/{namespace}',
    response_model=UpstreamResponse,
    tags=["Upstreams"],
    summary="특정 namespace의 Upstreams 조회",
    description="K8S 클러스터의 지정한 namespace의 Service를 불러옵니다.",
    responses={
        200: {"description": "Upstreams가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_namespace_upstreams(namespace: str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/services",
            headers=k8s.API_HEADER, 
            )
        response_json = orjson.loads(response.text)
        
        items_data = [
            UpstreamItem(
                uid=item.get("metadata", {}).get("uid", ""),
                name=item.get("metadata", {}).get("name", ""),
                namespace=item.get("metadata", {}).get("namespace", ""),
                ports=[port.get("port", 0) for port in item.get("spec", {}).get("ports", [])]
            )
            for item in response_json.get("items", [])
        ]
            
    return UpstreamResponse(data=items_data)

@router.post(
    '/',
    tags=["Upstreams"],
    summary="클러스터 외부 연결 Upstream 생성",
    description="외부 연결 Service를 생성합니다.",
    responses={
        200: {"description": "Upstreams가 성공적으로 생성됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def create_upstreams(request: UpstreamCreateRequest):
    service_manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": request.name,
            "namespace": request.namespace,
            "labels" : {
                "upstream": "external"
            }
        },
        "spec": {
            "ports": [{"port": request.service_port, "targetPort": request.target_port}]
        }
    }

    endpoints_manifest = {
        "apiVersion": "v1",
        "kind": "Endpoints",
        "metadata": {
            "name": request.name,
            "namespace": request.namespace
        },
        "subsets": [{
            "addresses": [{"ip": ip} for ip in request.external_ips],
            "ports": [{"port": request.target_port}]
        }]
    }

    async with httpx.AsyncClient(verify=False) as client:
        svc_response = await client.post(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{request.namespace}/services",
            headers=k8s.API_HEADER,
            json=service_manifest
            )
        
        ep_response = await client.post(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{request.namespace}/endpoints",
            headers=k8s.API_HEADER,
            json=endpoints_manifest
        )

    if svc_response.status_code != 201 or ep_response.status_code != 201:
        return JSONResponse(
            status_code=400,
            content={"message": "Upstream 생성 실패", "details": {
                "service": svc_response.text,
                "endpoints": ep_response.text
            }}
        )

    return JSONResponse(
        status_code=201,
        content={"message": f"{request.namespace} 네임스페이스에 {request.name} Upstream이 성공적으로 생성되었습니다."}
    )

    
@router.delete(
    '/',
    tags=["Upstreams"],
    summary="클러스터 외부 연결 Upstream 삭제",
    description="이름을 기반으로 네임스페이스를 탐색한 후, Upstream(Service & Endpoints)을 삭제합니다.",
    responses={
        200: {"description": "Upstream이 성공적으로 삭제됨"},
        404: {"description": "Upstream을 찾을 수 없음"},
        400: {"description": "잘못된 요청"}
    }
)
async def delete_upstreams(name: str):
    async with httpx.AsyncClient(verify=False) as client:
        # 클러스터 내 모든 Service 조회
        response = await client.get(
            url="https://kubernetes.default.svc.cluster.local/api/v1/services",
            headers=k8s.API_HEADER
        )
        response_json = orjson.loads(response.text)

        # 이름이 name과 일치하는 Service 찾기
        found_svc = next(
            (
                item for item in response_json.get("items", [])
                if item["metadata"]["name"] == name
                and item.get("metadata", {}).get("labels", {}).get("upstream") == "external"
            ),
            None
        )

        # 해당하는 Service가 없으면 404 반환
        if not found_svc:
            return JSONResponse(
                status_code=404,
                content={"message": f"외부 Upstream '{name}'를 찾을 수 없습니다."}
            )

        namespace = found_svc["metadata"]["namespace"]

        # Endpoints 삭제
        ep_response = await client.delete(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/endpoints/{name}",
            headers=k8s.API_HEADER
        )

        # Service 삭제
        svc_response = await client.delete(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/services/{name}",
            headers=k8s.API_HEADER
        )

    # Endpoints와 Service 삭제 결과 확인
    ep_status = ep_response.status_code
    svc_status = svc_response.status_code

    if ep_status == 404 and svc_status == 404:
        return JSONResponse(
            status_code=404,
            content={"message": f"Upstream '{name}'를 찾을 수 없습니다."}
        )

    if ep_status not in [200, 202, 204] or svc_status not in [200, 202, 204]:
        return JSONResponse(
            status_code=400,
            content={"message": "Upstream 삭제 실패", "details": {
                "endpoints": ep_response.text,
                "service": svc_response.text
            }}
        )

    return JSONResponse(
        status_code=200,
        content={"message": f"Upstream '{name}'가 성공적으로 삭제되었습니다."}
    )

@router.put(
    "/{name}",
    tags=["Upstreams"],
    summary="외부 Upstream 업데이트",
    description="K8S 클러스터의 기존 외부 Upstream(Service & Endpoints)을 업데이트합니다.",
    responses={
        200: {"description": "Upstream이 성공적으로 업데이트됨"},
        404: {"description": "Upstream을 찾을 수 없음"},
        400: {"description": "잘못된 요청"}
    }
)
async def update_upstreams(name: str, request: UpstreamUpdateRequest):
    async with httpx.AsyncClient(verify=False) as client:
        # 클러스터 내 모든 Service 조회
        response = await client.get(
            url="https://kubernetes.default.svc.cluster.local/api/v1/services",
            headers=k8s.API_HEADER
        )
        response_json = orjson.loads(response.text)

        # 이름이 name과 일치하는 외부 Service 찾기
        found_svc = next(
            (
                item for item in response_json.get("items", [])
                if item["metadata"]["name"] == name
                and item.get("metadata", {}).get("labels", {}).get("upstream") == "external"
            ),
            None
        )

        # 해당하는 Service가 없으면 404 반환
        if not found_svc:
            raise HTTPException(
                status_code=404, 
                detail=f"외부 Upstream '{name}'를 찾을 수 없습니다."
            )

        # 원본 서비스의 실제 이름과 네임스페이스 추출
        vs_name = found_svc["metadata"]["name"]
        namespace = found_svc["metadata"]["namespace"]

        # Service와 Endpoints의 개별 리소스 버전 획득
        service_resource_version = found_svc['metadata']['resourceVersion']
        
        # Endpoints 리소스 버전 조회
        ep_response = await client.get(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/endpoints/{vs_name}",
            headers=k8s.API_HEADER
        )
        endpoints_resource_version = orjson.loads(ep_response.text)['metadata']['resourceVersion']

        # 업데이트할 Service 매니페스트 준비
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": vs_name,
                "namespace": namespace,
                "resourceVersion": service_resource_version,
                "labels": {
                    "upstream": "external"
                }
            },
            "spec": {
                "ports": [{"port": request.service_port, "targetPort": request.target_port}]
            }
        }

        # 업데이트할 Endpoints 매니페스트 준비
        endpoints_manifest = {
            "apiVersion": "v1",
            "kind": "Endpoints",
            "metadata": {
                "name": vs_name,
                "namespace": namespace,
                "resourceVersion": endpoints_resource_version
            },
            "subsets": [{
                "addresses": [{"ip": ip} for ip in request.external_ips],
                "ports": [{"port": request.target_port}]
            }]
        }

        # Service 업데이트 요청
        svc_response = await client.put(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/services/{vs_name}",
            headers=k8s.API_HEADER,
            json=service_manifest
        )

        # Endpoints 업데이트 요청
        ep_response = await client.put(
            url=f"https://kubernetes.default.svc.cluster.local/api/v1/namespaces/{namespace}/endpoints/{vs_name}",
            headers=k8s.API_HEADER,
            json=endpoints_manifest
        )

        # 업데이트 결과 확인
        if svc_response.status_code not in [200, 201] or ep_response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=400,
                detail=f"Upstream 업데이트 실패: Service - {svc_response.text}, Endpoints - {ep_response.text}"
            )

        return JSONResponse(
            status_code=200,
            content={"message": f"{namespace} 네임스페이스의 {vs_name} Upstream이 성공적으로 업데이트되었습니다."}
        )