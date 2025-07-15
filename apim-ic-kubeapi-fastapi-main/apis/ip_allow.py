import json
import setting.k8s as k8s
from schema.ip import Allow
from temp import ip_ac_tmp 

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

import re
import httpx
import orjson
import requests


router = APIRouter(
    prefix="/kubeapi/ipallow"
)

@router.get(
    '/',
    tags=["IPAllow"],
    summary="IP Allow 정책 전체 조회",
    description="현재 NGINX Ingress Controller의 IP Allow Access Control 정책을 조회합니다.",
    responses={
        200: {"description": "IP Allow 정책이 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_ip_allow():
    a = requests.get(k8s.DB_URL_Policy)
    return JSONResponse(
        status_code = a.status_code,
        content={
                 "data" : json.loads(a.text)
            }
    )

@router.get(
    '/{policy_id}',
    tags=["IPAllow"],
    summary="IP Allow 정책 세부 조회",
    description="현재 NGINX Ingress Controller의 IP Allow Access Control 정책을 조회합니다.",
    responses={
        200: {"description": "IP Allow 정책이 성공적으로 조회됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def read_ip_allow(policy_id : str):
    a = requests.get(k8s.DB_URL_Policy+policy_id)
    return JSONResponse(
        status_code = a.status_code,
        content={
                 "data" : json.loads(a.text)
            }
    )

    # async with httpx.AsyncClient(verify=False) as client:
        # response = await client.get(
        #         url=k8s.API_URL_POLICY+'?labelSelector=type=ip-allow',
        #         headers=k8s.API_HEADER, 
        #     )
        # response_json = orjson.loads(response.text)

        # items_data = []
        
        # for item in response_json.get("items", []):
        #     name = item.get("metadata", {}).get("name")
        #     uid = item.get("metadata", {}).get("uid")
        #     allow_ips = item.get("spec", {}).get("accessControl", {}).get("allow", [])
        #     items_data.append({
        #         "uid": uid,
        #         "name": name,
        #         "allow_ips": allow_ips
        #     })
            
    # return JSONResponse(
    #     status_code=response.status_code,
    #     content={
    #              "data" : items_data
    #         }
    # )
    # return k8s.api_url+'?labelSelector=type=ip'

@router.post(
    "/",
    tags=["IPAllow"],
    summary="IP Allow 정책 추가",
    description="현재 NGINX Ingress Controller의 IP Allow Access Control 정책을 추가합니다.",
    responses={
        201: {"description": "IP Allow 정책이 성공적으로 등록됨"},
        400: {"description": "잘못된 요청"},
        409: {"description": "이름이 동일 한 정책이 이미 존재함"}
    },
    status_code=201
)
async def create_ip_allow(body_data : Allow):
    # if(body_data.ApplyRange == "http"):
    #     AppendData = ""
        
    #     async with httpx.AsyncClient(verify=False) as client:
            
    #         response = await client.get(
    #                 url = k8s.API_URL_CONFIGMAP,
    #                 headers = k8s.API_HEADER
    #             )
            
    #         ori_data = response.json()["data"]["http-snippets"]
    #         print(re.findall(r"allow\s([\d./]+)",ori_data))
    #         for AllowIP in body_data.AllowIP :
    #             if AllowIP in re.findall(r"allow\s([\d./]+)",ori_data) :
    #                 return JSONResponse(
    #                     status_code=status.HTTP_409_CONFLICT,
    #                     content={"message": status.HTTP_409_CONFLICT}
    #                 ) 
                
    #         AppendData = ' '.join([f"allow {IP};" for IP in body_data.AllowIP])
            
    #         k8s_body_data = ip_ac_tmp.ip_scope_http_create(ori_data, AppendData)
            
    #         response = await client.put(    
    #                 url = k8s.API_URL_CONFIGMAP,
    #                 headers = k8s.API_HEADER,
    #                 json=k8s_body_data
    #         )
    #         if(response.status_code==200):
    #             return JSONResponse(
    #                 status_code=status.HTTP_201_CREATED,
    #                 content={"message": status.HTTP_201_CREATED}
    #             ) 
    #         return JSONResponse(
    #             status_code=response.status_code,
    #             content={"message": response.status_code}
    #         )
                    
    # elif(body_data.ApplyRange == "server" or body_data.ApplyRange == "location"): 
        
    k8s_body_data = ip_ac_tmp.ip_allow_json(body_data.PolicyName, body_data.AllowIP)
    
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
                    url = k8s.API_URL_POLICY,
                    headers = k8s.API_HEADER, 
                    json = k8s_body_data
                )
        if(response.status_code > 299):
            return JSONResponse(
                status_code=response.status_code,
                content={"message": response.status_code}
            )
        data = response.json()
        uid = data.get('metadata', {}).get('uid', None)
        print(uid)
        
        database = requests.post(k8s.DB_URL_Policy,json=ip_ac_tmp.ip_al_db_cu(body_data,uid))
        if(database.status_code > 299):
            return JSONResponse(
                status_code=database.status_code,
                content={"message": database.status_code}
            )
        return JSONResponse(
            status_code=database.status_code,
            content={"message": database.status_code}
        )
    
            

@router.put(
    "/{policy_name}",
    tags=["IPAllow"],
    summary="IP Allow 정책 업데이트(수정)",
    description="현재 NGINX Ingress Controller의 IP Allow Access Control 정책을 업데이트(수정)합니다.",
    responses={
        200: {"description": "IP Allow 정책이 성공적으로 업데이트(수정)됨"},
        400: {"description": "잘못된 요청"},
    }
)
async def update_ip_allow(policy_name : str ,body_data: dict):
    body_data = Allow(PolicyName=policy_name, **body_data)
    # if(body_data.ApplyRange == "http"): 
    #     async with httpx.AsyncClient(verify=False) as client:
    #         response = await client.get(
    #             url = k8s.API_URL_CONFIGMAP,
    #             headers = k8s.API_HEADER_UPDATE, 
    #         )
            
    #         ori_data = response.json()["data"]["http-snippets"]
    #         ori_data = re.findall(r"allow\s([\d./]+)",ori_data)
    #         update_data = []
            
    #         for AllowIP in body_data.AllowIP :
    #             if body_data.PatchIP in ori_data :
    #                 update_data = body_data.AllowIP
    #                 print(update_data)
    #                 continue
    #             update_data = ori_data
    #             print(update_data)
                        
                    
    #         update_data = ' '.join([f"allow {IP};" for IP in update_data])
    #         k8s_body_data = ip_ac_tmp.ip_scope_http_update(update_data)
            
    #         response = await client.patch(
    #             url = k8s.API_URL_CONFIGMAP,
    #             headers = k8s.API_HEADER_UPDATE, 
    #             json=k8s_body_data
    #         )

        
    # elif(body_data.ApplyRange == "server" or body_data.ApplyRange == "location"):
    k8s_body_data = ip_ac_tmp.ip_allow_json(policy_name, body_data.AllowIP)
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.patch(
            url = k8s.API_URL_POLICY + policy_name +"-ip-allow",
            headers = k8s.API_HEADER_UPDATE, 
            json=k8s_body_data
        )
        print(response.text)
        if (response.status_code > 299):
            return JSONResponse(
                status_code=response.status_code,
                content={"message": response.status_code}
            )
        data = response.json()
        uid = data.get('metadata', {}).get('uid', None)
    database = requests.put(k8s.DB_URL_Policy+uid,json=ip_ac_tmp.ip_al_db_cu(body_data,uid))
    return JSONResponse(
        status_code=database.status_code,
        content={"message": database.status_code}
    )
    # return JSONResponse(
    #         status_code=response.status_code,
    #         content={"message": response.status_code}
    #     )
    

@router.delete(
    "/{policy_name}",
    tags=["IPAllow"],
    summary="IP Allow 정책 삭제",
    description="현재 NGINX Ingress Controller의 IP Allow Access Control 정책을 삭제합니다.",
    responses={
        201: {"description": "IP Allow 정책이 성공적으로 삭제됨"},
        400: {"description": "잘못된 요청"}
    }
)
async def delete_ip_allow(policy_name : str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.delete(
            url = k8s.API_URL_POLICY + policy_name + "-ip-allow",
            headers = k8s.API_HEADER
        )
        if (response.status_code > 299):
            return JSONResponse(
                status_code=response.status_code,
                content={"message": response.status_code}
            )
    data = response.json()
    uid = data.get('details', {}).get('uid', None)
    # print(data)
    # print(uid)
    database = requests.delete(k8s.DB_URL_Policy+uid)
    return JSONResponse(
            status_code=database.status_code,
            content={"message": database.status_code}
        ) 
    
    