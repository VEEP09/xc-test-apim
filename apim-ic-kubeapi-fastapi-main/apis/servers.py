import setting.k8s as k8s
from schema.server import VirtualServerSpec, VirtualServerMetadata, VirtualServerResponse, VirtualServerListResponse, Upstream, Policy, Route, CreateServerRequest

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import httpx
import orjson

router = APIRouter(
    prefix="/kubeapi/servers"
)

@router.get(
    '/',
    response_model=VirtualServerListResponse,
    tags=["Servers"],
    summary="Servers 전체 조회",
    description="K8S 클러스터의 VirtualServer를 불러옵니다.",
    responses={
        200: {"description": "Servers가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_servers():
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL_VIRTUALSERVER,
            headers=k8s.API_HEADER, 
            )
        response_json = response.json()

        servers = []

        for item in response_json.get("items", []):
            servers.append(
                VirtualServerResponse(
                    metadata=VirtualServerMetadata(
                        uid=item["metadata"]["uid"],
                        name=item["metadata"]["name"],
                        namespace=item["metadata"]["namespace"]
                    ),
                    spec=VirtualServerSpec(
                        host=item["spec"]["host"],
                        tls=item["spec"].get("tls"),
                        policies=[Policy(**p) for p in item["spec"].get("policies", [])],
                        upstreams=[Upstream(**u) for u in item["spec"].get("upstreams", [])],
                        routes=[Route(**r) for r in item["spec"].get("routes", [])]
                    )
                )
            )

    return VirtualServerListResponse(data=servers)

@router.get(
    '/{namespace}',
    response_model=VirtualServerListResponse,
    tags=["Servers"],
    summary="특정 namespace의 Servers 조회",
    description="K8S 클러스터의 지정한 namespace의 VirtualServer를 불러옵니다.",
    responses={
        200: {"description": "Servers가 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_namespace_servers(namespace: str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=f"https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/namespaces/{namespace}/virtualservers",
            headers=k8s.API_HEADER, 
            )
        response_json = response.json()

        servers = []

        for item in response_json.get("items", []):
            servers.append(
                VirtualServerResponse(
                    metadata=VirtualServerMetadata(
                        uid=item["metadata"]["uid"],
                        name=item["metadata"]["name"],
                        namespace=item["metadata"]["namespace"]
                    ),
                    spec=VirtualServerSpec(
                        host=item["spec"]["host"],
                        tls=item["spec"].get("tls"),
                        policies=[Policy(**p) for p in item["spec"].get("policies", [])],
                        upstreams=[Upstream(**u) for u in item["spec"].get("upstreams", [])],
                        routes=[Route(**r) for r in item["spec"].get("routes", [])]
                    )
                )
            )

    return VirtualServerListResponse(data=servers)

@router.post(
    "/",
    tags=["Servers"],
    summary="Server 추가",
    description="K8S 클러스터에 VirtualServer를 생성합니다.",
    responses={
        201: {"description": "Server가 성공적으로 생성됨"},
        400: {"description": "잘못된 요청"},
        409: {"description": "이름이 동일한 Server가 이미 존재함"}
        }
)
async def create_servers(request: CreateServerRequest):

    name = request.name
    namespace = request.namespace
    server = request.spec

    virtual_server_data = {
        "apiVersion": "k8s.nginx.org/v1",
        "kind": "VirtualServer",
        "metadata": {
            "name": name,
            "namespace": namespace
        },
        "spec": {
            "host": server.host,
            "tls": server.tls.model_dump() if server.tls else None,  # tls가 있으면 처리
            "policies": [policy.model_dump() for policy in server.policies] if server.policies else [],
            "upstreams": [upstream.model_dump() for upstream in server.upstreams],
            "routes": [
                {
                    "path": route.path,
                    "policies": [policy.model_dump() for policy in route.policies] if route.policies else [],
                    "action": route.action #.model_dump(by_alias=True) // Action 모델 변경 시 수정
                }
                for route in server.routes
            ]
        }
    }

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            url=f"https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/namespaces/{namespace}/virtualservers",
            headers=k8s.API_HEADER,
            json=virtual_server_data
        )

    if response.status_code != 201:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Kubernetes API error: {response.text}"
        )

    return JSONResponse(
        status_code=response.status_code,
        content={"message": f"{name} Server가 {namespace} 네임스페이스에 성공적으로 생성됨"}
        )

@router.delete(
    "/",
    tags=["Servers"],
    summary="Server 삭제",
    description="K8S 클러스터의 특정 VirtualServer를 삭제합니다.",
    responses={
        200: {"description": "Server가 성공적으로 삭제됨"},
        404: {"description": "Server를 찾을 수 없음"},
        400: {"description": "잘못된 요청"}
    }
)
async def delete_server(name: str):
    # VirtualServer가 배포된 네임스페이스 탐색
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            url=k8s.API_URL_VIRTUALSERVER,
            headers=k8s.API_HEADER
        )
        response_json = response.json()
        
        found_vs = next(
            (item for item in response_json.get("items", []) 
             if item["metadata"]["name"] == name),
            None
        )

        # VirtualServer를 찾지 못한 경우 404 에러 발생
        if not found_vs:
            raise HTTPException(
                status_code=404, 
                detail=f"VirtualServer with name {name} not found"
            )

        # 찾은 VirtualServer의 namespace 추출
        vs_name = found_vs["metadata"]["name"]
        namespace = found_vs["metadata"]["namespace"]

        # VirtualServer 삭제
        delete_response = await client.delete(
            url=f"https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/namespaces/{namespace}/virtualservers/{vs_name}",
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
                "message": f"{namespace} 네임스페이스의 {name} Server가 성공적으로 삭제됨"
            }
        )
    
@router.put(
    "/{name}",
    tags=["Servers"],
    summary="Server 업데이트",
    description="K8S 클러스터의 기존 VirtualServer를 업데이트합니다.",
    responses={
        200: {"description": "Server가 성공적으로 업데이트됨"},
        404: {"description": "Server를 찾을 수 없음"},
        400: {"description": "잘못된 요청"}
    }
)
async def update_server(name: str, data: VirtualServerSpec):
    # VirtualServer 탐색
    async with httpx.AsyncClient(verify=False) as client:
        # 전체 VirtualServer 목록에서 해당 이름의 서버 찾기
        response = await client.get(
            url=k8s.API_URL_VIRTUALSERVER,
            headers=k8s.API_HEADER
        )
        response_json = response.json()
        
        # 원본 서버 찾기
        found_vs = next(
            (item for item in response_json.get("items", []) 
             if item["metadata"]["name"] == name),
            None
        )

        # VirtualServer를 찾지 못한 경우 404 에러 발생
        if not found_vs:
            raise HTTPException(
                status_code=404, 
                detail=f"VirtualServer with name {name} not found"
            )

        # 원본 서버의 실제 이름과 네임스페이스 추출
        vs_name = found_vs["metadata"]["name"]
        namespace = found_vs["metadata"]["namespace"]

        resource_version = found_vs['metadata']['resourceVersion']

        # 업데이트할 VirtualServer 데이터 준비
        virtual_server_data = {
            "apiVersion": "k8s.nginx.org/v1",
            "kind": "VirtualServer",
            "metadata": {
                "name": vs_name,
                "namespace": namespace,
                "resourceVersion": resource_version
            },
            "spec": {
                "host": data.host,
                "tls": data.tls.model_dump() if data.tls else None,
                "policies": [policy.model_dump() for policy in data.policies] if data.policies else [],
                "upstreams": [upstream.model_dump() for upstream in data.upstreams],
                "routes": [
                    {
                        "path": route.path,
                        "policies": [policy.model_dump() for policy in route.policies] if route.policies else [],
                        "action": route.action #.model_dump(by_alias=True) // Action 모델 변경 시 수정
                    }
                    for route in data.routes
                ]
            }
        }

        # VirtualServer 업데이트 요청
        update_response = await client.put(
            url=f"https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/namespaces/{namespace}/virtualservers/{vs_name}",
            headers=k8s.API_HEADER,
            json=virtual_server_data
        )

        if update_response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=update_response.status_code,
                detail=f"Kubernetes API error: {update_response.text}"
            )

        return JSONResponse(
            status_code=200,
            content={"message": f"{vs_name} Server가 {namespace} 네임스페이스에서 성공적으로 업데이트됨"}
        )
