from pydantic import BaseModel, Field
from typing import List, Optional

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
        
class Action(BaseModel):
    pass_: str = Field(..., alias="pass", description="요청을 전달할 Upstream")

    class Config:
        json_schema_extra = {
            "example": {
                "pass": "myapp"
            }
        }

class RouteItem(BaseModel):
    name: str = Field(..., description="Route 이름")
    path: str = Field("/", description="구성할 Path 정보")
    policies: Optional[List[Policy]] = []
    action: Action 

    class Config:
        json_schema_extra = {
            "example": {
                "name": "myroute",
                "path": "/route1",
                "policies": [Policy.Config.json_schema_extra["example"]],
                "action": Action.Config.json_schema_extra["example"]
            }
        }

class RouteResponse(BaseModel):
    data: List[RouteItem]