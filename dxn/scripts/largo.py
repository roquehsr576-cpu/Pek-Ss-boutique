import sys, subprocess, math
sys.path.insert(0,'/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
import motion as M
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
B='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'; L=B+'largo/'
W,H,FPS=1920,1080,30
fH=M.font('Inter-ExtraBold.otf',110); fB=M.font('Inter-ExtraBold.otf',76); fS=M.font('Inter-Bold.otf',44); fP=M.font('Inter-ExtraBold.otf',40)
bgimg=Image.open(B+'reel/s4.png').convert('RGB')
r=max(W*1.15/bgimg.width,H*1.15/bgimg.height); bgimg=bgimg.resize((int(bgimg.width*r),int(bgimg.height*r)),Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
bgimg=ImageEnhance.Brightness(bgimg).enhance(0.35)
emb=M.Embers(60)
def card(name, dur, lines):
    """lines: list of (text, font, color, y, start, pill)"""
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
      '-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',L+name],stdin=subprocess.PIPE)
    layers=[(M.text_layer(t,f,fill=c,pill=pl),y,s) for t,f,c,y,s,pl in lines]
    for n in range(int(dur*FPS)):
        t=n/FPS; bw,bh=bgimg.size; ox=(bw-W)/2+40*math.sin(t*0.4); oy=(bh-H)/2+20*math.sin(t*0.3)
        fr=bgimg.crop((int(ox),int(oy),int(ox)+W,int(oy)+H)).convert('RGBA')
        # emb uses 1080x1920 coords: draw on a temp and scale
        ov=Image.new('RGBA',(1080,1920),(0,0,0,0)); emb.draw(ov,t,alpha=0.9); fr.alpha_composite(ov.resize((W,int(1920*W/1080))).crop((0,0,W,H)))
        for i,(ly,y,s) in enumerate(layers):
            if t>=s:
                k=M.entrance(t,s); dy,sc,ang=M.idle(t,i*0.9,amp=4)
                a=M.clamp((t-s)/0.2)*M.exit_(t,dur,0.3)
                l=ly
                if abs(sc*(0.85+0.15*k)-1)>1e-3: l=ly.resize((int(ly.width*sc*(0.85+0.15*k)),int(ly.height*sc*(0.85+0.15*k))),Image.BILINEAR)
                if a<0.999: al=l.split()[3].point(lambda v:int(v*a)); l=l.copy(); l.putalpha(al)
                fr.alpha_composite(l,(int(W/2-l.width/2),int(y+70*(1-k)+dy-l.height/2)))
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
RED=(200,25,25,240); GOLD=(255,205,90)
which=sys.argv[1]
if which=='intro':
    card('c00.mp4',6,[('TODO SOBRE EL GANODERMA',fH,(255,255,255),400,0.1,None),('el hongo de 2,000 años que va en tu café',fS,GOLD,540,0.5,None),
                      ('Historia · cultivo · 3 recetas',fP,(255,255,255),680,0.9,RED)])
elif which=='outro':
    card('c99.mp4',7,[('¿CUÁL RECETA PRUEBAS PRIMERO?',fB,(255,255,255),380,0.1,None),('Cuéntame en los comentarios',fS,GOLD,500,0.5,None),
                      ('Suscríbete para más recetas con café de Ganoderma',fP,(255,255,255),640,0.9,RED),
                      ('Este producto no es un medicamento. El consumo de este producto es responsabilidad de quien lo recomienda y de quien lo usa.',M.font('Inter-Medium.otf',22),(210,210,210),960,1.2,None)])
else:
    i=int(which); titles=['CÓMO CRECE','SUS 6 FORMAS','LA HISTORIA DE DXN','DEL BOSQUE A TU TAZA','CAFÉ NEGRO + 3 RECETAS','FRAPPÉ EN 30 SEGUNDOS','VITA CAFÉ']
    card(f'c{i:02d}.mp4',3,[(f'CAPÍTULO {i}',fP,(255,255,255),420,0.05,RED),(titles[i-1],fH,GOLD,560,0.25,None)])
print('ok',which)
