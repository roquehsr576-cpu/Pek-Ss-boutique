import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/reel2/'
W,H,FPS=1080,1920,30; T=34.6; N=int(T*FPS)
F='/usr/share/fonts/opentype/inter/'
fonts={'huge':ImageFont.truetype(F+'Inter-ExtraBold.otf',190),'big':ImageFont.truetype(F+'Inter-ExtraBold.otf',88),
 'mid':ImageFont.truetype(F+'Inter-ExtraBold.otf',66),'small':ImageFont.truetype(F+'Inter-Bold.otf',46),'tiny':ImageFont.truetype(F+'Inter-SemiBold.otf',32)}
pillf=ImageFont.truetype(F+'Inter-ExtraBold.otf',60)
S=1.22; base={}
for i in range(0,6):
    im=ImageEnhance.Contrast(Image.open(R+f's{i}.png').convert('RGB')).enhance(1.05)
    base[i]=im.resize((int(W*S),int(H*S)),Image.LANCZOS)
sc=[(0,0,4.7,1.12,1.0),(1,4.4,12.4,1.0,1.16),(2,12.1,19.4,1.0,1.15),(3,19.1,24.5,1.0,1.18),(4,24.2,29.0,1.0,1.2),(5,28.7,T,1.0,1.12)]
XF=0.35
def frame_of(idx,t,s0,s1,z0,z1):
    p=max(0,min(1,(t-s0)/(s1-s0))); z=z0+(z1-z0)*(p*p*(3-2*p))
    b=base[idx]; bw,bh=b.size; cw=min(bw,W*S/z); ch=min(bh,H*S/z)
    x=(bw-cw)/2; y=(bh-ch)/2
    return b.resize((W,H),Image.BILINEAR,box=(x,y,x+cw,y+ch))
# (start,end,kind,text,y)
tx=[(0.1,2.3,'pill','PARTE 2',330),(2.4,4.6,'big','LA HISTORIA',330),
 (5.2,9.6,'big','+20 AÑOS DE\nINVESTIGACIÓN',300),
 (9.6,12.3,'big','LIM SIOW JIN',330),(10.0,12.3,'small','Fundador de DXN',460),
 (12.3,16.0,'huge','1993',300),(16.0,19.3,'big','KEDAH,\nMALASIA',300),
 (19.4,24.3,'mid','CULTIVAR\nPROCESAR\nLLEVAR AL MUNDO',280),
 (24.4,28.8,'huge','+20',260),(24.4,28.8,'mid','MILLONES',470),(24.9,28.8,'small','de distribuidores DXN\nen el mundo',570),(24.9,28.8,'tiny','*Cifra según DXN',1820),
 (29.0,31.9,'big','¿DEL BOSQUE\nA TU TAZA?',300),
 (31.9,T,'pill','PARTE 3',820),(32.2,T,'small','Síguenos para no perdértela',960)]
def draw_text(img,kind,txt,y0,a):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); A=int(255*a)
    if kind=='pill':
        w=d.textlength(txt,font=pillf); x=(W-w)/2
        d.rounded_rectangle((x-50,y0-26,x+w+50,y0+96),radius=60,fill=(200,25,25,int(235*a)))
        d.text((x,y0),txt,font=pillf,fill=(255,255,255,A))
    else:
        f=fonts[kind]; lh=f.size*1.15
        for k,l in enumerate(txt.split('\n')):
            w=d.textlength(l,font=f); d.text(((W-w)/2,y0+k*lh),l,font=f,fill=(255,255,255,A),stroke_width=max(2,f.size//14),stroke_fill=(0,0,0,int(A*0.85)))
    img=img.convert('RGBA'); img.alpha_composite(ov); return img.convert('RGB')
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',R+'video_mudo.mp4'],stdin=subprocess.PIPE)
for n in range(N):
    t=n/FPS; act=[s for s in sc if s[1]<=t<s[2]]
    fr=None
    for (i,s0,s1,z0,z1) in act:
        im=frame_of(i,t,s0,s1,z0,z1)
        a=1.0 if (s0==0 or t>=s0+XF) else (t-s0)/XF
        fr=im if fr is None else Image.blend(fr,im,a)
    if t>=32.0: fr=ImageEnhance.Brightness(fr).enhance(max(0.35,1-(t-32.0)/0.6))
    if 24.4<=t<24.7: fr=Image.blend(fr,Image.new('RGB',(W,H),(255,255,255)),0.35*(1-(t-24.4)/0.3))
    for (s0,s1,k,txt,y) in tx:
        if s0<=t<s1:
            a=min(1,(t-s0)/0.2,(s1-t)/0.15 if s1<T else 1); fr=draw_text(fr,k,txt,y,a)
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print('ok')
