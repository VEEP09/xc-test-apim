from pydantic import BaseModel, Field
from typing import List

class CertificateItem(BaseModel):
    name: str = Field(..., description="Secret 이름")
    namespace: str = Field(..., description="Secret 생성 네임스페이스")
    tls_crt: str = Field(..., description="TLS 인증서 파일")
    tls_key: str = Field(..., description="TLS 키 파일")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "example.com",
                "namespace": "default",
                "tls_crt": "-----BEGIN CERTIFICATE-----......=-----END CERTIFICATE-----",
                "tls_key": "-----BEGIN PRIVATE KEY-----......==-----END PRIVATE KEY-----"
            }
        }

class CertificateResponse(BaseModel):
    data: List[dict]