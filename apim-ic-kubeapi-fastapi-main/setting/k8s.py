K8S_JWT : str = open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r').readlines()[0]
            
API_URL_POLICY : str = 'https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/namespaces/nginx-ingress/policies/'

API_URL_CONFIGMAP = 'https://kubernetes.default.svc.cluster.local/api/v1/namespaces/nginx-ingress/configmaps/nginx-config/'

DB_URL_Policy = "http://175.196.233.106:8123/db/ipac/"

API_URL_SERVICE : str = 'https://kubernetes.default.svc.cluster.local/api/v1/services'

API_URL_VIRTUALSERVER : str = 'https://kubernetes.default.svc.cluster.local/apis/k8s.nginx.org/v1/virtualservers'

API_URL_TLS_SECRET : str = 'https://kubernetes.default.svc.cluster.local/api/v1/secrets'

API_HEADER : dict = {
    'Authorization' : 'Bearer '+ K8S_JWT,
    'Content-Type' : 'application/json'
    }

API_HEADER_UPDATE : dict = {
    'Authorization' : 'Bearer '+ K8S_JWT,
    'Content-Type' : 'application/merge-patch+json'
}
