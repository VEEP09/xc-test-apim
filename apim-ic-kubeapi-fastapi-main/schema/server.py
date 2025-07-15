from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class Policy(BaseModel):
    name: str = Field(..., description="적용할 Policy 이름")
    namespace: str = "nginx-ingress" # Policy는 해당 ns로 고정(NPIC 배포 ns)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ip-policy",
                "namespace": "nginx-ingress"
            }
        }

class Upstream(BaseModel):
    name: str
    service: str
    port: int

    class Config:
        json_schema_extra = {
            "example": {
                "name": "myapp",
                "service": "myapp-svc",
                "port": 80
            }
        }

class PassAction(BaseModel):
    pass_: str = Field(..., alias="pass", description="요청을 전달할 Upstream")

    class Config:
        json_schema_extra = {
            "example": {
                "pass": "myapp"
            }
        }

class Route(BaseModel):
    path: str
    policies: Optional[List[Policy]] = Field([], description="Route에 적용할 Policy 목록")
    action: Any # 추후 Pass|Proxy|Redirect|Return 구성

    class Config:
        json_schema_extra = {
            "example": {
                "path": "/app",
                "policies": [Policy.Config.json_schema_extra["example"]],
                "action": PassAction.Config.json_schema_extra["example"]
            }
        }

class TLSRedirect(BaseModel):
    enable: bool = Field(False, description="HTTP to HTTPS Redirect 적용 여부")
    code: Literal[301, 302, 307, 308] = Field(301, description="TLS Redirect 상태 코드")

    class Config:
        json_schema_extra = {
            "example": {
                "enable": True,
                "code": 301
            }
        }

class TLS(BaseModel):
    secret: str = Field(..., description="TLS 인증서 k8s Secret 이름")
    redirect: Optional[TLSRedirect] = Field(None, description="HTTP to HTTPS Redirect 적용 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "secret": "myapp-cert",
                "redirect": TLSRedirect.Config.json_schema_extra["example"]
            }
        }

class VirtualServerSpec(BaseModel):
    host: str
    tls: Optional[TLS] = None
    policies: Optional[List[Policy]] = []
    upstreams: List[Upstream]
    routes: Optional[List[Route]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "host": "www.example.com",
                "tls": TLS.Config.json_schema_extra["example"],
                "policies": [Policy.Config.json_schema_extra["example"]],
                "upstreams": [Upstream.Config.json_schema_extra["example"]],
                "routes": [Route.Config.json_schema_extra["example"]]
            }
        }

class CreateServerRequest(BaseModel):
    name: str
    namespace: str
    spec: VirtualServerSpec

    class Config:
        json_schema_extra = {
            "example": {
                "name": "example-server",
                "namespace": "default",
                "spec": VirtualServerSpec.Config.json_schema_extra["example"]
            }
        }
    
class VirtualServerMetadata(BaseModel):
    uid: str
    name: str
    namespace: str

    class Config:
        json_schema_extra = {
            "example": {
                "uid": "12347128-5a9c-4097-b911-105f3e512d2c",
                "name": "example-vs",
                "namespace": "default"
            }
        }

class VirtualServerResponse(BaseModel):
    metadata: VirtualServerMetadata
    spec: VirtualServerSpec

class VirtualServerListResponse(BaseModel):
    data: List[VirtualServerResponse]