import subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/reel/'
W,H,FPS=1080,1920,30; T=22.6; N=int(T*FPS)
F='/usr/share/fonts/opentype/inter/'
big=ImageFont.truetype(F+'Inter-ExtraBold.otf',92)
mid=ImageFont.truetype(F+'Inter-ExtraBold.otf',70)
pill=ImageFont.truetype(F+'Inter-ExtraBold.otf',64)
small=ImageFont.truetype(F+'Inter-Bold.otf',46)
S=1.22
base={}
for i in range(1,5):
    im=Image.open(R+f's{i}.png').convert('RGB')
    im=ImageEnhance.Contrast(im).enhance(1.06)
    base[i]=im.resize((int(W*S),int(H*S)),Image.LANCZOS)
dark=ImageEnhance.Brightness(base[4].filter(ImageFilter.GaussianBlur(10))).enhance(0.28)
base[5]=dark
# scenes: (img, start, end, zoom_from, zoom_to, panx)
sc=[(1,0,5.4,1.0,1.18,0),(2,5.2,7.6,1.05,1.18,0),(3,7.4,10.4,1.0,1.15,0),(4,10.2,17.9,1.0,1.2,0),(5,17.7,T,1.0,1.06,0)]
XF=0.35
def frame_of(idx,t,s0,s1,z0,z1):
    p=(t-s0)/(s1-s0); p=max(0,min(1,p)); z=z0+(z1-z0)*(p*p*(3-2*p))
    b=base[idx]; bw,bh=b.size
    cw,ch=bw/(S*z)*1.0*S/ S, 0
    cw=min(bw,W*S/z); ch=min(bh,H*S/z)
    x=(bw-cw)/2; y=(bh-ch)/2
    return b.resize((W,H),Image.BILINEAR,box=(x,y,x+cw,y+ch))
# texts: (start,end,kind,text)
tx=[(0.15,2.6,'big','¿QUÉ CREES\nQUE ES ESTO?'),
    (2.6,5.3,'pill','1 SEMANA'),
    (5.3,7.5,'pill','1 MES'),
    (7.5,10.3,'pill','2 MESES'),
    (10.3,11.6,'pill','3 MESES'),
    (11.6,14.3,'big','"EL REY DE\nLAS HIERBAS"'),
    (14.3,17.8,'mid','GANODERMA\nREISHI · LINGZHI'),
    (15.2,17.8,'small','+2,000 años de historia'),
    (18.2,20.1,'big','¿SABES PARA\nQUÉ SE USA?'),
    (19.9,T,'big','PARTE 2'),
    (20.3,T,'small','Síguenos para no perdértela'),]
def draw_text(img,kind,txt,a):
    if a<=0: return img
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    A=int(255*a)
    if kind=='pill':
        w=d.textlength(txt,font=pill); x=(W-w)/2; y=330
        d.rounded_rectangle((x-50,y-28,x+w+50,y+100),radius=64,fill=(200,25,25,int(235*a)))
        d.text((x,y),txt,font=pill,fill=(255,255,255,A))
    else:
        f={'big':big,'mid':mid,'small':small}[kind]
        y0={'big':300,'mid':300,'small':560}[kind]
        if kind=='big' and txt=='PARTE 2': y0=820
        if kind=='small' and 'Síguenos' in txt: y0=960
        lines=txt.split('\n'); lh=f.size*1.15
        for k,l in enumerate(lines):
            w=d.textlength(l,font=f); x=(W-w)/2; y=y0+k*lh
            d.text((x,y),l,font=f,fill=(255,255,255,A),stroke_width=max(3,f.size//14),stroke_fill=(0,0,0,int(A*0.85)))
    img=img.convert('RGBA'); img.alpha_composite(ov); return img.convert('RGB')
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',R+'video_mudo.mp4'],stdin=subprocess.PIPE)
for n in range(N):
    t=n/FPS
    act=[s for s in sc if s[1]<=t<s[2]]
    imgs=[]
    for (i,s0,s1,z0,z1,_) in act:
        a=1.0
        if t<s0+XF and s0>0: a=(t-s0)/XF
        imgs.append((frame_of(i,t,s0,s1,z0,z1),a))
    fr=imgs[0][0]
    for im,a in imgs[1:]: fr=Image.blend(fr,im,max(0,min(1,a)))
    # flash at reveal
    if 10.2<=t<10.5: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.35*(1-(t-10.2)/0.3))
    # vignette-ish top gradient for text legibility
    for (s0,s1,k,txt) in tx:
        if s0<=t<s1:
            a=min(1,(t-s0)/0.2, (s1-t)/0.15 if s1<T else 1)
            fr=draw_text(fr,k,txt,a)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print('ok')
