import json


toplevel_str = """
{
    "id": "v1",
    "type": "apiVersion",
    "links": {
        "accounts": "http://my.rancher.url/v1/accounts",
        "services": "http://my.rancher.url/v1/services"
    },
    "actions": {}
}
"""
toplevel_dict = json.loads(toplevel_str)


services_str = """
{
  "type":"collection",
  "resourceType":"service",
  "links":{
    "self":"http://my.rancher.url/v1/services"
  },
  "createTypes":{

  },
  "actions":{

  },
  "data":[
    {
      "id":"1s850",
      "type":"service",
      "links":{
        "self":"http://my.rancher.url/v1/services/1s850",
        "environment":"http://my.rancher.url/v1/services/1s850/environment",
        "instances":"http://my.rancher.url/v1/services/1s850/instances"
      },
      "actions":{
        "update":"http://my.rancher.url/v1/services/1s850/?action=update",
        "restart":"http://my.rancher.url/v1/services/1s850/?action=restart"
      },
      "name":"hi",
      "state":"active",
      "created":"2016-05-10T19:51:24Z",
      "createdTS":1462909884000,
      "data":{

      },
      "environmentId":"1e350",
      "kind":"service",
      "metadata":{
        "io.rancher.service.hash":"ba12a7430b9396e27c19a3d8382189d4a0bcaaa7"
      },
      "publicEndpoints":[
        {
          "ipAddress":"172.17.0.1",
          "port":58212,
          "serviceId":"1s850",
          "hostId":"1h1",
          "instanceId":"1i8338"
        }
      ],
      "scale":1,
      "uuid":"50cf50b1-cfd5-4cdd-abdd-99244facdeef"
    },
    {
      "id":"1s894",
      "type":"service",
      "links":{
        "self":"http://my.rancher.url/v1/services/1s894",
        "environment":"http://my.rancher.url/v1/services/1s894/environment",
        "instances":"http://my.rancher.url/v1/services/1s894/instances"
      },
      "actions":{
        "update":"http://my.rancher.url/v1/services/1s894/?action=update",
        "restart":"http://my.rancher.url/v1/services/1s894/?action=restart"
      },
      "name":"ho",
      "state":"active",
      "created":"2016-05-11T17:21:10Z",
      "createdTS":1462987270000,
      "data":{

      },
      "description":null,
      "environmentId":"1e373",
      "kind":"service",
      "metadata":{
        "io.rancher.service.hash":"4bb55bb307adf2bd794f4830b496b71210d64f56"
      },
      "publicEndpoints":null,
      "scale":1,
      "uuid":"5ae214bc-3514-4c79-aabb-aa5c5eb7a018"
    }
  ],
  "sortLinks":{
    "created":"http://my.rancher.url/v1/services?sort=created"
  },
  "pagination":{
    "limit":100,
    "partial":false
  },
  "sort":null,
  "filters":{
    "created":null
  },
  "createDefaults":{

  }
}
"""
services_dict = json.loads(services_str)


service_str = """
{
  "id":"1s850",
  "type":"service",
  "links":{
    "self":"http://my.rancher.url/v1/services/1s850",
    "environment":"http://my.rancher.url/v1/services/1s850/environment",
    "instances":"http://my.rancher.url/v1/services/1s850/instances"
  },
  "actions":{
    "update":"http://my.rancher.url/v1/services/1s850/?action=update",
    "restart":"http://my.rancher.url/v1/services/1s850/?action=restart"
  },
  "name":"hi",
  "state":"active",
  "created":"2016-05-10T19:51:24Z",
  "createdTS":1462909884000,
  "data":{

  },
  "environmentId":"1e350",
  "kind":"service",
  "metadata":{
    "io.rancher.service.hash":"ba12a7430b9396e27c19a3d8382189d4a0bcaaa7"
  },
  "publicEndpoints":[
    {
      "ipAddress":"172.17.0.1",
      "port":58212,
      "serviceId":"1s850",
      "hostId":"1h1",
      "instanceId":"1i8338"
    }
  ],
  "scale":1,
  "uuid":"50cf50b1-cfd5-4cdd-abdd-99244facdeef"
}
"""
service_dict = json.loads(service_str)
