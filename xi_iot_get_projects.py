import http.client
import json
import pprint

import xi_iot_env_constants

pp = pprint.PrettyPrinter()

class ResourceNotFound(Exception):
    
    def __init__(self, message):
        self.message = message

class Xi:
    resources = {}

    @classmethod
    def Resource(cls, resource_name):
        cls.resources['xi_iot'] = XiIoT()
        if resource_name in cls.resources:
            return cls.resources[resource_name]
        raise ResourceNotFound("Invalid resource name provided: %s" % resource_name) 

class XiIoT:
    def __init__(self):
        self.connection = None
        self.token = None

    def login(self, userEmail, userPwd):
        self.connection = http.client.HTTPSConnection(xi_iot_env_constants.xi_iot_api_endpoint)
        payload = '{\"email\":\"%s\",\"password\":\"%s\"}' % (userEmail, userPwd)
        headers = { 'content-type': "application/json" }
        self.connection.request("POST","/v1.0/login", payload, headers)
        resp = self.connection.getresponse()
        resp = json.loads(resp.read())
        self.token = resp['token']

    def get_projects(self):
        headers = { 'authorization': "Bearer %s" % self.token }
        self.connection.request("GET", "/v1.0/projects", headers=headers)
        resp = self.connection.getresponse()
        resp = json.loads(resp.read())
        projects = []
        for projectDict in resp['result']:
            projects.append(Project(projectDict))
        return projects

class Project:
    def __init__(self, adict):
        self.__dict__.update(adict)

class Application:
    def __init__(self, adict):
        self.__dict__.update(adict)

xi_iot = Xi.Resource("xi_iot")
xi_iot.login(xi_iot_env_constants.userEmail, xi_iot_env_constants.userPwd)
projects = xi_iot.get_projects()
for project in projects:
    pp.pprint("name: %s" % project.name)
    pp.pprint("  id: %s" % project.id)
    pp.pprint("  edgeIds: %s" % project.edgeIds)




