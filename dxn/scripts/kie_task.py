import json,sys,urllib.request
body=json.loads(sys.argv[1])
req=urllib.request.Request("https://api.kie.ai/api/v1/jobs/createTask",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
try: print(urllib.request.urlopen(req,timeout=40).read().decode())
except urllib.error.HTTPError as e: print(e.code,e.read().decode())
