import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W,H,FPS=1080,1920,30
F='/usr/share/fonts/opentype/inter/'
FONTS={'huge':ImageFont.truetype(F+'Inter-ExtraBold.otf',150),'big':ImageFont.truetype(F+'Inter-ExtraBold.otf',92),
 'mid':ImageFont.truetype(F+'Inter-ExtraBold.otf',68),'small':ImageFont.truetype(F+'Inter-Bold.otf',46),'tiny':ImageFont.truetype(F+'Inter-SemiBold.otf',38)}
PILL=ImageFont.truetype(F+'Inter-ExtraBold.otf',58)
S=1.2
def load_still(path,fit=False):
    im=Image.open(path).convert('RGB')
    if fit:  # place whole image over blurred cover background
        bg=im.resize((int(W*S),int(H*S))); r=max(W*S/im.width,H*S/im.height)
        bg=im.resize((int(im.width*r),int(im.height*r))).crop((0,0,int(W*S),int(H*S))).filter(ImageFilter.GaussianBlur(30))
        bg=ImageEnhance.Brightness(bg).enhance(0.55)
        k=W*S*0.92/im.width; fg=im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS)
        bg.paste(fg,((bg.width-fg.width)//2,(bg.height-fg.height)//2)); return bg
    r=max(W*S/im.width,H*S/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-int(W*S))//2; y=(im.height-int(H*S))//2
    return ImageEnhance.Contrast(im.crop((x,y,x+int(W*S),y+int(H*S)))).enhance(1.04)
def kb(b,p,z0,z1):
    z=z0+(z1-z0)*p; bw,bh=b.size; cw=min(bw,W*S/z); ch=min(bh,H*S/z); x=(bw-cw)/2; y=(bh-ch)/2
    return b.resize((W,H),Image.BILINEAR,box=(x,y,x+cw,y+ch))
class Clip:
    def __init__(s,path,start=0.0):
        s.p=subprocess.Popen(['ffmpeg','-loglevel','quiet','-ss',str(start),'-i',path,'-vf',f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
        s.last=None
    def next(s):
        b=s.p.stdout.read(W*H*3)
        if len(b)==W*H*3: s.last=Image.frombytes('RGB',(W,H),b)
        return s.last
def draw_text(img,kind,txt,y0,a,pop,color=(200,25,25)):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); A=int(255*a)
    if kind=='pill':
        w=d.textlength(txt,font=PILL); x=(W-w)/2
        d.rounded_rectangle((x-46,y0-24,x+w+46,y0+92),radius=58,fill=color+(int(235*a),))
        d.text((x,y0),txt,font=PILL,fill=(255,255,255,A))
    else:
        f=FONTS[kind]; lh=f.size*1.15
        if kind in ('small','tiny'):
            ls=txt.split('\n'); mw=max(d.textlength(l,font=f) for l in ls)
            d.rounded_rectangle(((W-mw)/2-36,y0-22,(W+mw)/2+36,y0+len(ls)*lh+14),radius=28,fill=(0,0,0,int(165*a)))
        for k,l in enumerate(txt.split('\n')):
            w=d.textlength(l,font=f); d.text(((W-w)/2,y0+k*lh),l,font=f,fill=(255,255,255,A),stroke_width=max(3,f.size//13),stroke_fill=(0,0,0,int(A*0.9)))
    if pop<1:
        sz=(int(W*pop),int(H*pop)); o2=ov.resize(sz,Image.BILINEAR); ov=Image.new('RGBA',(W,H),(0,0,0,0)); ov.alpha_composite(o2,((W-sz[0])//2,(H-sz[1])//2))
    img=img.convert('RGBA'); img.alpha_composite(ov); return img.convert('RGB')
def render(out,T,segs,texts,flashes=(),dark_from=None):
    """segs: list of (t0,t1,kind,obj,z0,z1) kind in 'clip','still'; texts: (t0,t1,kind,txt,y)"""
    N=int(T*FPS)
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
      '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    last=None
    for n in range(N):
        t=n/FPS; fr=None
        for (t0,t1,k,o,z0,z1) in segs:
            if t0<=t<t1:
                fr=o.next() if k=='clip' else kb(o,(t-t0)/(t1-t0),z0,z1)
                if fr is None: fr=last
                break
        if fr is None: fr=last
        last=fr
        if dark_from is not None and t>=dark_from: fr=ImageEnhance.Brightness(fr).enhance(max(0.3,1-(t-dark_from)/0.5))
        for c in flashes:
            if c<=t<c+0.1: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.5*(1-(t-c)/0.1))
        for (s0,s1,k,txt,y) in texts:
            if s0<=t<s1:
                e=t-s0; a=1.0 if s0==0 else min(1,e/0.08); a=min(a,(s1-t)/0.1 if s1<T else 1)
                pop=1.0 if (e>0.18 or s0==0) else 0.85+0.15*(e/0.18)
                fr=draw_text(fr,k,txt,y,max(0,a),pop)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
