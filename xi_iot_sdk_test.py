import unittest

import xi_iot_env_constants
from xi_iot_sdk import *

class TestXiIoTSDK(unittest.TestCase):

    def test_sdk(self):
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

if __name__ == '__main__':
    unittest.main()