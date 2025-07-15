def ip_allow_json(PolicyName : str, AllowIP : list):
    return {
                "apiVersion": "k8s.nginx.org/v1",
                "kind": "Policy",
                "metadata": {
                    "name": PolicyName+"-ip-allow",
                    "labels": {
                        "type":"ip-allow"
                    }
                },
                "spec": {
                    "accessControl": {
                        "allow": AllowIP 
                    }
                }
            }
    
    
def ip_deny_json(PolicyName : str, DenyIP : list):
    return {
                "apiVersion": "k8s.nginx.org/v1",
                "kind": "Policy",
                "metadata": {
                    "name": PolicyName+"-ip-deny",
                    "labels": {
                        "type":"ip-deny"
                    }
                },
                "spec": {
                    "accessControl": {
                        "deny": DenyIP 
                    }
                }
            }
    
def ip_scope_http_update(Data : str):
    return {
        "apiVersion": "v1",
        "data": {
            "http-snippets": Data,
            "resolver-addresses": "kube-dns.kube-system.svc.cluster.local",
            "resolver-valid": "5s",
            "zone-sync": "true"
        },
        "kind": "ConfigMap",
        "metadata": {
            "annotations": {},
            "name": "nginx-config",
            "namespace": "nginx-ingress"
        }
    }
    
def ip_scope_http_create(OriData : str, AppendData : str):
    return {
        "apiVersion": "v1",
        "data": {
            "http-snippets": OriData +" " + AppendData,
            "resolver-addresses": "kube-dns.kube-system.svc.cluster.local",
            "resolver-valid": "5s",
            "zone-sync": "true"
        },
        "kind": "ConfigMap",
        "metadata": {
            "annotations": {},
            "name": "nginx-config",
            "namespace": "nginx-ingress"
        }
    }
    


def ip_al_db_cu(body_data, uid : str):
    return {
         "PolicyName" : body_data.PolicyName+"-ip-allow",
         "Id" : uid,
         "IPArr" : list(body_data.AllowIP),
         "ApplyRange" : body_data.ApplyRange   
    }
    
def ip_dn_db_cu(body_data, uid : str):
    return {
         "PolicyName" : body_data.PolicyName+"-ip-deny",
         "Id" : uid,
         "IPArr" : list(body_data.DenyIP),
         "ApplyRange" : body_data.ApplyRange   
    }