import json,sys,urllib.request
prompt=open(sys.argv[1]).read(); url=sys.argv[2]
body={"prompt":prompt,"imageUrls":[url],"model":"veo3_fast","aspectRatio":"9:16","enableTranslation":False,"callBackUrl":"https://example.com/cb"}
req=urllib.request.Request("https://api.kie.ai/api/v1/veo/generate",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
try: print(urllib.request.urlopen(req,timeout=40).read().decode())
except urllib.error.HTTPError as e: print(e.code,e.read().decode())
