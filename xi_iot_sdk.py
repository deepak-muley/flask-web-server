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

