from routers.router import router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn



app = FastAPI(
    title="NGINX APIM with FastAPI",
    description="FastAPI 기반 KubeAPI Policy, Secret, Config 구성",
    version="0.1.0",
    openapi_tags=[
        {"name": "IPDeny", "description": "IPDeny Policy KubeAPI 구성"},
        {"name": "IPAllow", "description": "IPAllow Policy KubeAPI 구성"},
        {"name": "Oidc", "description": "Oidc Policy, Secret KubeAPI 구성(백엔드용)"},
        {"name": "Upstreams", "description": "API G/W Upstreams(k8s service) KubeAPI 구성"},
        {"name": "Routes", "description": "API G/W Routes 구성"},
        {"name": "Servers", "description": "API G/W Servers(k8s virtualserver) KubeAPI 구성"},
        {"name": "Certs", "description": "API G/W Certs(k8s tls-secret) KubeAPI 구성"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# Keycloak 라우터 추가
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)