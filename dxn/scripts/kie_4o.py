import json,sys,urllib.request
prompt=open(sys.argv[1]).read()
body={"prompt":prompt,"size":"2:3","nVariants":1,"isEnhance":False,"callBackUrl":"https://example.com/cb"}
req=urllib.request.Request("https://api.kie.ai/api/v1/gpt4o-image/generate",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
try: print(urllib.request.urlopen(req,timeout=40).read().decode())
except urllib.error.HTTPError as e: print(e.code,e.read().decode())
