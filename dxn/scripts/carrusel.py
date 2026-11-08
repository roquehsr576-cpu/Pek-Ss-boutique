from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
C='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/carrusel/'
OUT='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/out/'
W,H=1080,1350
F='/usr/share/fonts/opentype/inter/'
def f(n,s): return ImageFont.truetype(F+n,s)
T=f('Inter-ExtraBold.otf',78); T2=f('Inter-ExtraBold.otf',64); PN=f('Inter-ExtraBold.otf',44); PD=f('Inter-Medium.otf',32)
SM=f('Inter-SemiBold.otf',30); TINY=f('Inter-Medium.otf',22); PILL=f('Inter-Bold.otf',30)
def bg_photo(path):
    im=Image.open(path).convert('RGB'); r=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; return im.crop((x,y,x+W,y+H))
def grad(img,color,top=True,h=520,a0=235):
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for i in range(h):
        a=int(a0*(1-i/h)**1.3); y=i if top else H-1-i
        d.line((0,y,W,y),fill=color+(a,))
    img=img.convert('RGBA'); img.alpha_composite(ov); return img
def center(d,y,txt,font,fill=(255,255,255),stroke=0,sf=(0,0,0)):
    for k,l in enumerate(txt.split('\n')):
        w=d.textlength(l,font=font); d.text(((W-w)/2,y+k*font.size*1.12),l,font=font,fill=fill,stroke_width=stroke,stroke_fill=sf)
def pill(d,y,txt,bgc,fg=(255,255,255)):
    w=d.textlength(txt,font=PILL); x=(W-w)/2
    d.rounded_rectangle((x-30,y-12,x+w+30,y+48),radius=30,fill=bgc); d.text((x,y),txt,font=PILL,fill=fg)
def cards(img,items,accent,y0):
    d=ImageDraw.Draw(img); n=len(items); ch=150; gap=22
    y=y0 if y0 else H-60-n*ch-(n-1)*gap-40
    for name,desc in items:
        d.rounded_rectangle((70,y,W-70,y+ch),radius=30,fill=(255,255,255,240))
        d.rounded_rectangle((70,y,90,y+ch),radius=10,fill=accent)
        d.text((120,y+26),name,font=PN,fill=(30,30,30)); d.text((120,y+86),desc,font=PD,fill=(85,85,85))
        y+=ch+gap
    return d
slides=[
 dict(img='c1.png',color=(20,70,40),q='¿CUÁL CAFÉ DXN\nES PARA TI?',sub='Desliza y descubre el tuyo  →',items=[]),
 dict(img='c2.png',color=(20,20,20),q='¿PREFIERES SIN\nAZÚCAR AÑADIDA?',items=[('Lingzhi Black Coffee 2 en 1','Intenso y aromático, sin azúcar añadida'),('Cream Coffee','Cremoso y sedoso, sin azúcar añadida')],accent=(200,160,60)),
 dict(img='c3.png',color=(120,80,45),q='¿TE GUSTA CREMOSO\nY SUAVE?',items=[('Lingzhi Coffee 3 en 1 Lite','Suave, cremoso y con cuerpo'),('White Coffee Zhino','Estilo capuchino con espuma cremosa')],accent=(190,130,70)),
 dict(img='c4.png',color=(70,40,25),q='¿ERES DE\nCHOCOLATE?',items=[('Zhi Mocha','Café con cocoa en polvo'),('Cocozhi','Bebida de cocoa para toda la familia')],accent=(150,90,50)),
 dict(img='c5.png',color=(35,20,12),q='¿TE GUSTA EL\nCAFÉ FUERTE?',items=[('Zhi Roasted Coffee','Café tostado: sabor intenso')],accent=(200,25,25)),
 dict(img='c6.png',color=(50,110,50),q='¿NO TOMAS\nCAFÉ?',items=[('Lingzhi Tea Latte','Té cremoso y menos amargo'),('Lemonzhi','Limón y té: refrescante')],accent=(230,190,30)),
]
for i,s in enumerate(slides,1):
    im=grad(bg_photo(C+s['img']),s['color'],True,560,240)
    if s['items']: im=grad(im,(0,0,0),False,520,150)
    d=ImageDraw.Draw(im)
    if i>1: pill(d,58,f'¿CUÁL CAFÉ DXN ES PARA TI?  ·  {i}/7',(200,25,25))
    center(d,150 if i>1 else 90,s['q'],T,stroke=2,sf=(0,0,0))
    if s['items']: cards(im,s['items'],s['accent'],None)
    else:
        d.rounded_rectangle((W/2-260,H-170,W/2+260,H-100),radius=35,fill=(200,25,25)); center(d,H-157,s['sub'],SM)
    if i>1: d.text((W-170,40),'Desliza →',font=TINY,fill=(255,255,255))
    im.convert('RGB').save(OUT+f'carrusel_{i}.jpg',quality=93)
# slide 7
im=Image.new('RGB',(W,H),(20,70,40)); d=ImageDraw.Draw(im)
for y in range(H): d.line((0,y,W,y),fill=(int(14+20*y/H),int(60+30*y/H),int(34+14*y/H)))
pf=Image.open(OUT+'foto_perfil_dxn_800.jpg').convert('RGB').resize((520,520),Image.LANCZOS)
m=Image.new('L',(2080,2080),0); ImageDraw.Draw(m).ellipse((0,0,2079,2079),fill=255); m=m.resize((520,520),Image.LANCZOS)
d.ellipse((W/2-272,318,W/2+272,862),fill=(120,220,90)); im.paste(pf,(int(W/2-260),330),m)
pill(d,58,'¿CUÁL CAFÉ DXN ES PARA TI?  ·  7/7',(200,25,25))
center(d,140,'¿YA SABES CUÁL\nES EL TUYO?',T2)
center(d,895,'Roque Hernández',PN,fill=(255,255,255)); center(d,955,'Distribuidor DXN',SM,fill=(190,235,180))
d.rounded_rectangle((110,1025,W-110,1160),radius=40,fill=(255,255,255))
center(d,1043,'Escríbeme por mensaje',PN,fill=(20,70,40)); center(d,1103,'y te ayudo a elegir',SM,fill=(80,80,80))
center(d,1230,'Este producto no es un medicamento. El consumo de este producto es\nresponsabilidad de quien lo recomienda y de quien lo usa.',TINY,fill=(200,225,200))
im.save(OUT+'carrusel_7.jpg',quality=93)
print('ok')
