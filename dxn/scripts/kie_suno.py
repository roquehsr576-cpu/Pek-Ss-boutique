import json,sys,time,urllib.request
tid=sys.argv[1]
for _ in range(40):
    d=json.load(urllib.request.urlopen(f"https://api.kie.ai/api/v1/generate/record-info?taskId={tid}",timeout=30))
    dd=d.get('data') or {}; st=dd.get('status')
    songs=((dd.get('response') or {}).get('sunoData') or [])
    if st in ('SUCCESS',) or 'FAIL' in str(st) or 'ERROR' in str(st):
        print(st,dd.get('errorMessage'))
        for s in songs: print(s.get('id'),s.get('duration'),s.get('audioUrl'))
        break
    time.sleep(8)
else: print('timeout',st)
print(urllib.request.urlopen("https://api.kie.ai/api/v1/chat/credit").read().decode())
