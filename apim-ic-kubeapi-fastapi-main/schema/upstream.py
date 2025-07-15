from pydantic import BaseModel, Field
from typing import List

class UpstreamItem(BaseModel):
    uid: str = Field(..., description="Service K8S uid")
    name: str = Field(..., description="Service 이름")
    namespace: str = Field(..., description="Service 배포 네임스페이스")
    ports: List[int] = Field(..., description="Service 포트 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "uid": "12347128-5a9c-4097-b911-105f3e512d2c",
                "name": "example-svc",
                "namespace": "default",
                "ports": [80, 443]
            }
        }

class UpstreamCreateRequest(BaseModel):
    name: str = Field(..., description="생성할 Service 이름")
    namespace: str = Field(..., description="Service 배포 네임스페이스")
    external_ips: List[str] = Field(..., description="연결할 외부 IP 목록")
    service_port: int = Field(..., description="Service 포트")
    target_port: int = Field(..., description="대상 포트")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "external-svc",
                "namespace": "default",
                "external_ips": ["192.168.100.10", "192.168.100.11"],
                "service_port": 80,
                "target_port": 8080
            }
        }

class UpstreamUpdateRequest(BaseModel):
    external_ips: List[str] = Field(..., description="연결할 외부 IP 목록")
    service_port: int = Field(..., description="Service 포트")
    target_port: int = Field(..., description="대상 포트")

    class Config:
        json_schema_extra = {
            "example": {
                "external_ips": ["192.168.100.10", "192.168.100.11"],
                "service_port": 80,
                "target_port": 8080
            }
        }

class UpstreamResponse(BaseModel):
    data: List[UpstreamItem]