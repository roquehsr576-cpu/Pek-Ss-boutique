import json,sys,time,urllib.request
ids=sys.argv[1:]; res={}
for _ in range(80):
    for t in ids:
        if t in res: continue
        d=json.load(urllib.request.urlopen(f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={t}",timeout=30)).get('data') or {}
        if d.get('status') in ('SUCCESS','CREATE_TASK_FAILED','GENERATE_FAILED'):
            res[t]=(d.get('status'),d.get('errorMessage'),(d.get('response') or {}).get('resultUrls'))
    if len(res)==len(ids): break
    time.sleep(8)
for t in ids: print(t,res.get(t,'pending'))
print(urllib.request.urlopen("https://api.kie.ai/api/v1/chat/credit").read().decode())
