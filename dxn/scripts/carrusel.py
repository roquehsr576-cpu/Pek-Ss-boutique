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
PROD='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/carrusel/prod/'
def pack(key,bw,bh):
    im=Image.open(PROD+key+'.png'); im.thumbnail((bw,bh),Image.LANCZOS)
    sh=Image.new('RGBA',(im.width+30,im.height+30),(0,0,0,0)); a=im.split()[3].point(lambda v:int(v*0.35))
    sh.paste((0,0,0,255),(15,22),a); sh=sh.filter(ImageFilter.GaussianBlur(8)); sh.alpha_composite(im,(15,15)); return sh
def cards(img,items,accent,y0):
    d=ImageDraw.Draw(img); n=len(items); ch=230; gap=20
    y=H-50-n*ch-(n-1)*gap
    for name,desc,key in items:
        d.rounded_rectangle((60,y,W-60,y+ch),radius=30,fill=(255,255,255,245))
        d.rounded_rectangle((60,y,80,y+ch),radius=10,fill=accent)
        pk=pack(key,230,200); img.alpha_composite(pk,(int(100+(240-pk.width)/2),int(y+(ch-pk.height)/2)))
        tx=360; nf=PN if d.textlength(name,font=PN)<W-60-tx-30 else f('Inter-ExtraBold.otf',36)
        d.text((tx,y+58),name,font=nf,fill=(30,30,30))
        d.text((tx,y+122),desc,font=f('Inter-Medium.otf',28),fill=(85,85,85))
        y+=ch+gap
    return d
slides=[
 dict(img='c1.png',color=(20,70,40),q='¿CUÁL CAFÉ DXN\nES PARA TI?',sub='Desliza y descubre el tuyo  →',items=[]),
 dict(img='c2.png',color=(20,20,20),q='¿PREFIERES SIN\nAZÚCAR AÑADIDA?',items=[('Lingzhi Black Coffee 2 en 1','Intenso, sin azúcar añadida','black'),('Cream Coffee','Cremoso, sin azúcar añadida','cream')],accent=(200,160,60)),
 dict(img='c3.png',color=(120,80,45),q='¿TE GUSTA CREMOSO\nY SUAVE?',items=[('Lingzhi Coffee 3 en 1 Lite','Suave, cremoso y con cuerpo','lite'),('White Coffee Zhino','Estilo capuchino con espuma','zhino')],accent=(190,130,70)),
 dict(img='c4.png',color=(70,40,25),q='¿ERES DE\nCHOCOLATE?',items=[('Zhi Mocha','Café con cocoa en polvo','mocha'),('Cocozhi','Cocoa para toda la familia','cocozhi')],accent=(150,90,50)),
 dict(img='c5.png',color=(35,20,12),q='¿TE GUSTA EL\nCAFÉ FUERTE?',items=[('Zhi Roasted Coffee','Café tostado: sabor intenso','roasted')],accent=(200,25,25)),
 dict(img='c6.png',color=(50,110,50),q='¿NO TOMAS\nCAFÉ?',items=[('Lingzhi Tea Latte','Té cremoso y menos amargo','tealatte'),('Lemonzhi','Limón y té: refrescante','lemonzhi')],accent=(230,190,30)),
]
for i,s in enumerate(slides,1):
    im=grad(bg_photo(C+s['img']),s['color'],True,560,240)
    if s['items']: im=grad(im,(0,0,0),False,600,170)
    d=ImageDraw.Draw(im)
    if i>1: pill(d,58,f'¿CUÁL CAFÉ DXN ES PARA TI?  ·  {i}/7',(200,25,25))
    center(d,150 if i>1 else 90,s['q'],T,stroke=2,sf=(0,0,0))
    if s['items']: cards(im,s['items'],s['accent'],None)
    else:
        d.rounded_rectangle((W/2-260,H-170,W/2+260,H-100),radius=35,fill=(200,25,25)); center(d,H-157,s['sub'],SM)
    if i>1: d.text((W-170,40),'Desliza →',font=TINY,fill=(255,255,255))
    im.convert('RGB').save(OUT+f'carrusel_{i}.jpg',quality=93)
# slide 7: product lineup
im=Image.new('RGBA',(W,H),(20,70,40,255)); d=ImageDraw.Draw(im)
for y in range(H): d.line((0,y,W,y),fill=(int(14+20*y/H),int(60+30*y/H),int(34+14*y/H),255))
pill(d,58,'¿CUÁL CAFÉ DXN ES PARA TI?  ·  7/7',(200,25,25))
center(d,140,'¿YA SABES CUÁL\nES EL TUYO?',T2)
d.rounded_rectangle((50,300,W-50,1010),radius=40,fill=(255,255,255,245))
keys=['black','cream','lite','zhino','mocha','cocozhi','roasted','tealatte','lemonzhi']
cw,chh=(W-100)//3,230
for n,k in enumerate(keys):
    pk=pack(k,cw-40,chh-30); cx=50+(n%3)*cw+(cw-pk.width)//2; cy=315+(n//3)*chh+(chh-pk.height)//2
    im.alpha_composite(pk,(int(cx),int(cy)))
d.rounded_rectangle((110,1045,W-110,1180),radius=40,fill=(200,25,25))
center(d,1062,'Escríbeme por mensaje',PN); center(d,1122,'y te ayudo a elegir',SM,fill=(255,225,225))
center(d,1232,'Este producto no es un medicamento. El consumo de este producto es\nresponsabilidad de quien lo recomienda y de quien lo usa.',TINY,fill=(200,225,200))
im.convert('RGB').save(OUT+'carrusel_7.jpg',quality=93)
print('ok')
