import http.client
import json
import pprint

pp = pprint.PrettyPrinter()

userEmail = "test@test.com"
userPwd = "test"
conn = http.client.HTTPSConnection("iot.nutanix.com")
payload = '{\"email\":\"%s\",\"password\":\"%s\"}' % (userEmail, userPwd)
headers = { 'content-type': "application/json" }
conn.request("POST","/v1.0/login", payload, headers)
res = conn.getresponse()
data = json.loads(res.read())
pp.pprint(data)
print('\n')

headers = { 'authorization': "Bearer %s" % data["token"] }
conn.request("GET", "/v1.0/projects", headers=headers)
res = conn.getresponse()
data = json.loads(res.read())
pp.pprint(data)

