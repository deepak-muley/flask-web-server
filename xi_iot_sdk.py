import http.client
import json
import pprint

import xi_iot_env_constants

pp = pprint.PrettyPrinter()

class ResourceNotFound(Exception):
    
    def __init__(self, message):
        self.message = message 

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

    def get_applications(self):
        headers = { 'authorization': "Bearer %s" % self.token }
        self.connection.request("GET", "/v1.0/applications", headers=headers)
        resp = self.connection.getresponse()
        resp = json.loads(resp.read())
        apps = []
        for appDict in resp['result']:
            apps.append(Application(appDict))
        return apps

class Project:
    def __init__(self, adict):
        self.__dict__.update(adict)

    def create_application(self, appObject):
        xiIot = Xi.Resource('xi_iot')
        payload = json.dumps(appObject.__dict__)
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("POST", "/v1.0/applications", payload, headers)
        resp = xiIot.connection.getresponse()
        resp = json.loads(resp.read())
        pp.pprint(resp)
        return resp['id']

class Application:
    def __init__(self, adict):
        self.__dict__.update(adict)

class Xi:
    resources = {}
    xiIoT = XiIoT()

    @classmethod
    def Resource(cls, resource_name):
        cls.resources['xi_iot'] = cls.xiIoT
        if resource_name in cls.resources:
            return cls.resources[resource_name]
        raise ResourceNotFound("Invalid resource name provided: %s" % resource_name)

if __name__ == "__main__":
    xi_iot = Xi.Resource("xi_iot")
    xi_iot.login(xi_iot_env_constants.userEmail, xi_iot_env_constants.userPwd)
    projects = xi_iot.get_projects()
    for project in projects:
        pp.pprint("Project name: %s" % project.name)
        pp.pprint("--id: %s" % project.id)
        pp.pprint("--edgeIds: %s" % project.edgeIds)
        print("\n")

    apps = xi_iot.get_applications()
    for app in apps:
        pp.pprint("Application name: %s" % app.name)
        pp.pprint("--id: %s" % app.id)
        print("\n")

    project = projects[0]
    appDict = {}
    yamlFile = open("./flask-web-server.yaml", "r") 
    appDict['appManifest'] = yamlFile.read()
    appDict['name'] = "flask-web-server2"
    appDict['description'] = "test api created app"
    appDict['projectId'] = project.id
    app = Application(appDict)
    appId = project.create_application(app)
    pp.pprint("Application with Id %s created." % appId)



