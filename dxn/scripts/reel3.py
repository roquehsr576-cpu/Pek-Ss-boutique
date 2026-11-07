import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
R='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/reel3/'
W,H,FPS=1080,1920,30; T=22.6; N=int(T*FPS)
F='/usr/share/fonts/opentype/inter/'
fonts={'huge':ImageFont.truetype(F+'Inter-ExtraBold.otf',150),'big':ImageFont.truetype(F+'Inter-ExtraBold.otf',96),
 'mid':ImageFont.truetype(F+'Inter-ExtraBold.otf',70),'small':ImageFont.truetype(F+'Inter-Bold.otf',48)}
pillf=ImageFont.truetype(F+'Inter-ExtraBold.otf',58)
class Clip:
    def __init__(s,path,speed=1.0):
        s.p=subprocess.Popen(['ffmpeg','-loglevel','error','-i',R+path,'-vf',f'setpts={1/speed}*PTS,fps={FPS},scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
        s.last=None
    def next(s):
        b=s.p.stdout.read(W*H*3)
        if len(b)==W*H*3: s.last=Image.frombytes('RGB',(W,H),b)
        return s.last
S=1.2
def still(path):
    return ImageEnhance.Contrast(Image.open(R+path).convert('RGB')).enhance(1.05).resize((int(W*S),int(H*S)),Image.LANCZOS)
st={'mature':still('mature.png'),'harvest':still('harvest.png'),'powder':still('powder.png')}
def kb(name,t,s0,s1,z0,z1):
    p=max(0,min(1,(t-s0)/(s1-s0))); z=z0+(z1-z0)*p
    b=st[name]; bw,bh=b.size; cw=min(bw,W*S/z); ch=min(bh,H*S/z); x=(bw-cw)/2; y=(bh-ch)/2
    return b.resize((W,H),Image.BILINEAR,box=(x,y,x+cw,y+ch))
hook=Clip('hook.mp4'); stir=Clip('stir.mp4',speed=1.0)
tx=[(0.0,1.55,'big','¿TOMARÍAS\nCAFÉ...',300),(1.55,3.0,'big','...CON UN\nHONGO?',300),
 (3.0,5.0,'pill','NO ES BROMA',340),(5.0,6.7,'mid','ASÍ LLEGA\nA TU TAZA',300),
 (6.7,9.3,'pill','1 · SE COSECHA',300),(9.3,12.6,'pill','2 · SE SECA Y SE MUELE',300),
 (12.6,14.8,'pill','3 · SE MEZCLA CON CAFÉ',300),(14.8,17.4,'big','CAFÉ DE\nGANODERMA',300),
 (17.4,18.5,'big','¿YA LO\nPROBASTE?',620),(18.5,T,'mid','ESCRÍBEME',560),(18.5,T,'huge','"CAFÉ"',660),(19.0,T,'small','y te cuento más',860)]
def draw_text(img,kind,txt,y0,a,pop):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); A=int(255*a)
    if kind=='pill':
        w=d.textlength(txt,font=pillf); x=(W-w)/2
        d.rounded_rectangle((x-46,y0-24,x+w+46,y0+92),radius=58,fill=(200,25,25,int(235*a)))
        d.text((x,y0),txt,font=pillf,fill=(255,255,255,A))
    else:
        f=fonts[kind]; lh=f.size*1.12
        for k,l in enumerate(txt.split('\n')):
            w=d.textlength(l,font=f); d.text(((W-w)/2,y0+k*lh),l,font=f,fill=(255,255,255,A),stroke_width=max(3,f.size//13),stroke_fill=(0,0,0,int(A*0.9)))
    if pop<1:
        sz=(int(W*pop),int(H*pop)); o2=ov.resize(sz,Image.BILINEAR); ov=Image.new('RGBA',(W,H),(0,0,0,0)); ov.alpha_composite(o2,((W-sz[0])//2,(H-sz[1])//2))
    img=img.convert('RGBA'); img.alpha_composite(ov); return img.convert('RGB')
out=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',R+'video_mudo.mp4'],stdin=subprocess.PIPE)
prev=None
for n in range(N):
    t=n/FPS
    if t<5.0: fr=hook.next()
    elif t<6.7: fr=kb('mature',t,5.0,6.7,1.25,1.0)
    elif t<9.3: fr=kb('harvest',t,6.7,9.3,1.0,1.15)
    elif t<12.6: fr=kb('powder',t,9.3,12.6,1.15,1.0)
    elif t<17.4: fr=stir.next()
    else:
        fr=ImageEnhance.Brightness(stir.last).enhance(max(0.3,1-(t-17.4)/0.5))
    # quick white flash on hard cuts
    for c in (5.0,6.7,9.3,12.6):
        if c<=t<c+0.1: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.5*(1-(t-c)/0.1))
    for (s0,s1,k,txt,y) in tx:
        if s0<=t<s1:
            e=t-s0; a=1.0 if s0==0 else min(1,e/0.08); a=min(a,(s1-t)/0.1 if s1<T else 1)
            pop=1.0 if e>0.18 else 0.85+0.15*(e/0.18)
            if s0==0: pop=1.0
            fr=draw_text(fr,k,txt,y,max(0,a),pop)
    out.stdin.write(fr.tobytes())
out.stdin.close(); out.wait(); print('ok')
