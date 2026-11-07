import json,sys,time,urllib.request
ids=sys.argv[1:]; done={}
for _ in range(90):
    for t in ids:
        if t in done: continue
        d=json.load(urllib.request.urlopen(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={t}",timeout=30)).get('data') or {}
        st=d.get('state')
        if st in ('success','fail'):
            done[t]=(st,d.get('failMsg'),d.get('resultJson'),d.get('costTime'))
    if len(done)==len(ids): break
    time.sleep(8)
for t in ids: print(t,done.get(t,'pending'))
print(urllib.request.urlopen("https://api.kie.ai/api/v1/chat/credit").read().decode())
