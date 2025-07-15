from pydantic import BaseModel, Field
from typing import List

class Allow(BaseModel):
    PolicyName: str = Field(..., description="정책 이름")
    AllowIP: List[str] = Field(..., description="허용 할 IP")
    ApplyRange: str = Field(..., description="적용 범위(All, servers, routes)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "PolicyName": "example-policy",
                "AllowIP": ["192.168.201.1","192.168.201.1","192.168.201.1"],
                "ApplyRange": "http"
            }
        }


class Deny(BaseModel):
    PolicyName: str = Field(..., description="정책 이름")
    DenyIP: List[str] = Field(..., description="거부 할 IP")
    ApplyRange: str = Field(..., description="적용 범위(All, servers, routes)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "PolicyName": "example-policy",
                "DenyIP": ["192.168.201.1","192.168.201.1","192.168.201.1"],
                "DenyRange": "http"
            }
        }
        
