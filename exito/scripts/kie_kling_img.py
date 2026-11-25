import json,sys,urllib.request
prompt=open(sys.argv[1]).read().strip(); url=sys.argv[2]; dur=sys.argv[3] if len(sys.argv)>3 else "5"
body={"model":"kling-2.6/image-to-video","callBackUrl":"https://example.com/cb","input":{"prompt":prompt,"image_urls":[url],"duration":dur,"sound":False}}
req=urllib.request.Request("https://api.kie.ai/api/v1/jobs/createTask",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
try: print(urllib.request.urlopen(req,timeout=40).read().decode())
except urllib.error.HTTPError as e: print(e.code,e.read().decode())
