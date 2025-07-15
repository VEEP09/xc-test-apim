{
    "data": {
        "apiVersion": "k8s.nginx.org/v1",
        "items": [
            {
                "apiVersion": "k8s.nginx.org/v1",
                "kind": "Policy",
                "metadata": {
                    "creationTimestamp": "2025-03-21T05:18:45Z",
                    "generation": 1,
                    "labels": {
                        "type": "ip-allow"
                    },
                    "managedFields": [
                        {
                            "apiVersion": "k8s.nginx.org/v1",
                            "fieldsType": "FieldsV1",
                            "fieldsV1": {
                                "f:status": {
                                    ".": {},
                                    "f:message": {},
                                    "f:reason": {},
                                    "f:state": {}
                                }
                            },
                            "manager": "nginx-ingress",
                            "operation": "Update",
                            "subresource": "status",
                            "time": "2025-03-21T05:18:45Z"
                        },
                        {
                            "apiVersion": "k8s.nginx.org/v1",
                            "fieldsType": "FieldsV1",
                            "fieldsV1": {
                                "f:metadata": {
                                    "f:labels": {
                                        ".": {},
                                        "f:type": {}
                                    }
                                },
                                "f:spec": {
                                    ".": {},
                                    "f:accessControl": {
                                        ".": {},
                                        "f:allow": {}
                                    }
                                }
                            },
                            "manager": "python-httpx",
                            "operation": "Update",
                            "time": "2025-03-21T05:18:45Z"
                        }
                    ],
                    "name": "test-ip-allow",
                    "namespace": "nginx-ingress",
                    "resourceVersion": "2799405",
                    "uid": "69ca5a69-7cde-4f26-a5bd-08e36f942a61"
                },
                "spec": {
                    "accessControl": {
                        "allow": [
                            "192.168.201.1",
                            "192.22.22.1"
                        ]
                    }
                },
                "status": {
                    "message": "Policy nginx-ingress/test-ip-allow was added or updated",
                    "reason": "AddedOrUpdated",
                    "state": "Valid"
                }
            },
            {
                "apiVersion": "k8s.nginx.org/v1",
                "kind": "Policy",
                "metadata": {
                    "creationTimestamp": "2025-03-21T05:22:06Z",
                    "generation": 1,
                    "labels": {
                        "type": "ip-allow"
                    },
                    "managedFields": [
                        {
                            "apiVersion": "k8s.nginx.org/v1",
                            "fieldsType": "FieldsV1",
                            "fieldsV1": {
                                "f:status": {
                                    ".": {},
                                    "f:message": {},
                                    "f:reason": {},
                                    "f:state": {}
                                }
                            },
                            "manager": "nginx-ingress",
                            "operation": "Update",
                            "subresource": "status",
                            "time": "2025-03-21T05:22:06Z"
                        },
                        {
                            "apiVersion": "k8s.nginx.org/v1",
                            "fieldsType": "FieldsV1",
                            "fieldsV1": {
                                "f:metadata": {
                                    "f:labels": {
                                        ".": {},
                                        "f:type": {}
                                    }
                                },
                                "f:spec": {
                                    ".": {},
                                    "f:accessControl": {
                                        ".": {},
                                        "f:allow": {}
                                    }
                                }
                            },
                            "manager": "python-httpx",
                            "operation": "Update",
                            "time": "2025-03-21T05:22:06Z"
                        }
                    ],
                    "name": "test1212",
                    "namespace": "nginx-ingress",
                    "resourceVersion": "2799983",
                    "uid": "7c554a79-f348-4ca5-a81a-9de5dd983e00"
                },
                "spec": {
                    "accessControl": {
                        "allow": [
                            "192.168.201.1",
                            "192.22.22.1"
                        ]
                    }
                },
                "status": {
                    "message": "Policy nginx-ingress/test1212 was added or updated",
                    "reason": "AddedOrUpdated",
                    "state": "Valid"
                }
            }
        ],
        "kind": "PolicyList",
        "metadata": {
            "continue": "",
            "resourceVersion": "2801061"
        }
    }
}