from apis.ip_allow import router as ip_allow_router
from apis.ip_deny import router as ip_deny_router
from apis.upstreams import router as upstreams_router
from apis.routes import router as routes_router
from apis.servers import router as servers_router
from apis.certs import router as certs_router

from fastapi import APIRouter


router = APIRouter()

router.include_router(ip_allow_router)
router.include_router(ip_deny_router)
router.include_router(upstreams_router)
router.include_router(routes_router)
router.include_router(servers_router)
router.include_router(certs_router)