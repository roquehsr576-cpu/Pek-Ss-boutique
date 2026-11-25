import json,sys,time,urllib.request
ids=sys.argv[1:]; res={}
for _ in range(100):
    for t in ids:
        if t in res: continue
        d=json.load(urllib.request.urlopen(f"https://api.kie.ai/api/v1/veo/record-info?taskId={t}",timeout=30)).get('data') or {}
        f=d.get('successFlag')
        if f in (1,2,3): res[t]=(f,d.get('errorMessage'),(d.get('response') or {}).get('resultUrls'))
    if len(res)==len(ids): break
    time.sleep(10)
for t in ids: print(t,res.get(t,'pending'))
