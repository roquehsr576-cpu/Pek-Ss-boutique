import sys,json,subprocess
sys.path.insert(0,'/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from engine import *
V='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scratchpad/vita/'
OUT='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/out/'
words=[w for w in json.load(open(V+'words.json'))['words'] if w.get('type')=='word']
# group into captions of <=3 words, breaking after punctuation
caps=[];cur=[]
for w in words:
    cur.append(w)
    if len(cur)>=3 or w['text'][-1] in '.,?!':
        caps.append((cur[0]['start'],cur[-1]['end'],' '.join(x['text'] for x in cur))); cur=[]
if cur: caps.append((cur[0]['start'],cur[-1]['end'],' '.join(x['text'] for x in cur)))
caps=[(s, (caps[i+1][0] if i+1<len(caps) and caps[i+1][0]-e<0.6 else e+0.25), t) for i,(s,e,t) in enumerate(caps)]
KEY=('VITA','CAFÉ','GINSENG','TONGKAT','ALI','GANODERMA','SEIS','UNO','DXN','ORGÁNICO','CALIDAD','TAZA','MENSAJE','FAVORITO','DIFÍCIL')
CAP=ImageFont.truetype(F+'Inter-ExtraBold.otf',70)
def draw_caption(img,txt):
    d=ImageDraw.Draw(img); words=txt.upper().split(); y=1540
    widths=[d.textlength(w+' ',font=CAP) for w in words]; x=(W-sum(widths))/2
    for w,wd in zip(words,widths):
        core=w.strip('¡!¿?.,')
        col=(255,214,10) if core in KEY else (255,255,255)
        d.text((x,y),w,font=CAP,fill=col,stroke_width=6,stroke_fill=(0,0,0)); x+=wd
    return img
T_SPEECH=28.53; T=31.8
# background: blurred, darkened version of the avatar frame; avatar scaled to width 1080
src=subprocess.Popen(['ffmpeg','-loglevel','quiet','-i',V+'avatar.mp4','-vf',f'fps={FPS}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
aw,ah=784,1168; sh=int(ah*W/aw); top=(H-sh)//2
pack=Image.open(V+'vita_cut.png'); pack.thumbnail((620,800),Image.LANCZOS)
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',V+'vita_mudo.mp4'],stdin=subprocess.PIPE)
last=None
for n in range(int(T*FPS)):
    t=n/FPS
    if t<T_SPEECH:
        b=src.stdout.read(aw*ah*3)
        if len(b)==aw*ah*3: last=Image.frombytes('RGB',(aw,ah),b)
        fr=last.resize((W,sh),Image.BILINEAR)
        bg=last.resize((W,H)).filter(ImageFilter.GaussianBlur(25)); bg=ImageEnhance.Brightness(bg).enhance(0.6)
        bg.paste(fr,(0,top)); img=bg
        # top hook / info pills
        if t<4.4: img=draw_text(img,'big','¿POR QUÉ ES EL\nFAVORITO\nDE MUCHOS?',40,min(1,t/0.15),1.0)
        elif 7.9<=t<11.9: img=draw_text(img,'mid','CAFÉ + GINSENG\n+ TONGKAT ALI\n+ GANODERMA',40,1.0,1.0)
        elif 11.0<=t<14.0: img=draw_text(img,'pill','6 EN 1 · SOLO AGUA CALIENTE',110,1.0,1.0)
        elif 14.4<=t<19.2: img=draw_text(img,'mid','¿POR QUÉ SE CULTIVA\nEL GANODERMA?',60,1.0,1.0)
        elif 19.4<=t<25.6: img=draw_text(img,'mid','PROCESO ORGÁNICO\nY CONTROL DE CALIDAD',60,1.0,1.0)
        for s,e,txt in caps:
            if s<=t<e: img=draw_caption(img,txt)
    else:
        # end card
        img=Image.new('RGB',(W,H)); d=ImageDraw.Draw(img)
        for y in range(H): d.line((0,y,W,y),fill=(int(60+40*y/H),int(35+20*y/H),int(15+8*y/H)))
        e=min(1,(t-T_SPEECH)/0.3); sc=0.85+0.15*e
        pk=pack.resize((int(pack.width*sc),int(pack.height*sc)),Image.LANCZOS)
        img=img.convert('RGBA'); img.alpha_composite(pk,((W-pk.width)//2,330+int((800-pk.height)/2))); img=img.convert('RGB')
        img=draw_text(img,'big','¿YA PROBASTE\nTU VITA HOY?',90,1.0,1.0)
        img=draw_text(img,'pill','ESCRÍBEME POR MENSAJE',1250,1.0,1.0)
        img=draw_text(img,'tiny','Este producto no es un medicamento.\nEl consumo de este producto es responsabilidad\nde quien lo recomienda y de quien lo usa.',1640,1.0,1.0)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait(); print('ok',len(caps))
