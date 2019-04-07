import http.client
import json
import pprint

import xi_iot_env_constants

pp = pprint.PrettyPrinter()

class ResourceNotFound(Exception):
    def __init__(self, message):
        self.message = message 

class APIFailed(http.client.HTTPException):
    pass

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
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        self.token = resp['token']

    def list_projects(self):
        headers = { 'authorization': "Bearer %s" % self.token }
        self.connection.request("GET", "/v1.0/projects", headers=headers)
        resp = self.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        projects = []
        for projectDict in resp['result']:
            projects.append(Project(projectDict))
        return projects

    def list_applications(self):
        headers = { 'authorization': "Bearer %s" % self.token }
        self.connection.request("GET", "/v1.0/applications", headers=headers)
        resp = self.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        apps = []
        for appDict in resp['result']:
            apps.append(Application(appDict))
        return apps

    def list_all_application_statuses(self):
        headers = { 'authorization': "Bearer %s" % self.token }
        self.connection.request("GET", "/v1.0/applicationstatuses", headers=headers)
        resp = self.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        app_statuses = []
        for app_status in resp['result']:
            app_statuses.append(app_status)
        return app_statuses

class Project:
    def __init__(self, adict):
        self.__dict__.update(adict)

    def create_application(self, appObject):
        xiIot = Xi.Resource('xi_iot')
        payload = json.dumps(appObject.__dict__)
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("POST", "/v1.0/applications", payload, headers)
        resp = xiIot.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        return resp['id']

    def get_application(self, appId):
        xiIot = Xi.Resource('xi_iot')
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("GET", "/v1.0/applications/%s" % appId, headers=headers)
        resp = xiIot.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        return Application(resp)

    def update_application(self, appId, appObject):
        xiIot = Xi.Resource('xi_iot')
        payload = json.dumps(appObject.__dict__)
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("PUT", "/v1.0/applications/%s" % appId, payload, headers)
        resp = xiIot.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        return resp['id']

    def delete_application(self, appId):
        xiIot = Xi.Resource('xi_iot')
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("DELETE", "/v1.0/applications/%s" % appId, headers=headers)
        resp = xiIot.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        return resp['id']

    def list_edges(self):
        xiIot = Xi.Resource('xi_iot')
        headers = { 'authorization': "Bearer %s" % xiIot.token }
        xiIot.connection.request("GET", "/v1.0/projects/%s/edges" % self.id, headers=headers)
        resp = xiIot.connection.getresponse()
        if (resp.status != 200):
            raise APIFailed(resp.status, resp.reason, resp.read())
        resp = json.loads(resp.read())
        apps = []
        for appDict in resp['result']:
            apps.append(Application(appDict))
        return apps

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
    projects = xi_iot.list_projects()
    for project in projects:
        pp.pprint("Project name: %s" % project.name)
        pp.pprint("--id: %s" % project.id)
        pp.pprint("--edgeIds: %s" % project.edgeIds)
        print("\n")

    apps = xi_iot.list_applications()
    for app in apps:
        pp.pprint("Application name: %s" % app.name)
        pp.pprint("--id: %s" % app.id)
        print("\n")

    project = projects[0]
    edges = project.list_edges()
    edgeIds = []
    for edge in edges:
        pp.pprint("Edge name: %s" % edge.name)
        pp.pprint("--id: %s" % edge.id)
        edgeIds.append(edge.id)
        print("\n")

    with open("./flask-web-server.yaml", "r") as yamlFile:
        yamlData = yamlFile.read()

    #Create App
    appDict = {}
    appDict['appManifest'] = yamlData
    appDict['name'] = "flask-web-server"
    appDict['description'] = "test api created app"
    appDict['projectId'] = project.id
    appDict['edgeIds'] = edgeIds
    app = Application(appDict)
    appId = project.create_application(app)
    pp.pprint("Application with Id %s created." % appId)
    print("\n")

    app2Dict = {}
    app2Dict['appManifest'] = yamlData
    app2Dict['name'] = "flask-web-server2"
    app2Dict['description'] = "test api created app"
    app2Dict['projectId'] = project.id
    app2Dict['edgeIds'] = edgeIds
    app2 = Application(app2Dict)
    app2Id = project.create_application(app2)
    pp.pprint("Application with Id %s created." % app2Id)
    print("\n")

    #Get App
    app = project.get_application(appId)
    pp.pprint("Get Application Info with Id %s" % appId)
    pp.pprint("Application Details: %s" % app.__dict__)
    print("\n")

    #Get App statuses
    app_statuses = xi_iot.list_all_application_statuses()
    while len(app_statuses) == 0:
        pp.pprint("app status: %s" % app_statuses)
        app_statuses = xi_iot.list_all_application_statuses()
    for app_status in app_statuses:
        pp.pprint("Application status: %s" % app_status)
        print("\n")

    #Update App
    appDict = {}
    appDict['appManifest'] = yamlData
    appDict['name'] = "flask-web-server5"
    appDict['description'] = "test api created app 5"
    appDict['projectId'] = project.id
    appDict['edgeIds'] = edgeIds
    app = Application(appDict)
    appId = project.update_application(appId, app)
    pp.pprint("Application with Id %s updated." % appId)
    print("\n")

    #Delete App
    appDict = {}
    appDict['projectId'] = project.id
    appDict['id'] = appId
    app = Application(appDict)
    appId = project.delete_application(appId)
    pp.pprint("Application with Id %s deleted." % appId)
    print("\n")

    #Delete App2
    app2Dict = {}
    app2Dict['projectId'] = project.id
    app2Dict['id'] = app2Id
    app2 = Application(app2Dict)
    app2Id = project.delete_application(app2Id)
    pp.pprint("Application with Id %s deleted." % app2Id)
    print("\n")

