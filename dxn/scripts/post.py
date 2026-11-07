import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
B='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
W,H=1080,1350
F='/usr/share/fonts/opentype/inter/'
def f(n,s): return ImageFont.truetype(F+n,s)
src=Image.open(B+'images/5.webp').convert('RGB')
# background: blurred photo + dark green overlay
bg=src.resize((H,H)).crop(((H-W)//2,0,(H-W)//2+W,H)).filter(ImageFilter.GaussianBlur(28))
bg=Image.blend(bg,Image.new('RGB',(W,H),(10,48,28)),0.72)
d=ImageDraw.Draw(bg)
# circular profile photo
D=560
ph=src.resize((D,D),Image.LANCZOS)
m=Image.new('L',(D*4,D*4),0); ImageDraw.Draw(m).ellipse((0,0,D*4-1,D*4-1),fill=255); m=m.resize((D,D),Image.LANCZOS)
cx=(W-D)//2; cy=60
d.ellipse((cx-8,cy-8,cx+D+8,cy+D+8),fill=(120,220,90))
bg.paste(ph,(cx,cy),m)
def ctext(y,t,font,fill):
    w=d.textlength(t,font=font); d.text(((W-w)/2,y),t,font=font,fill=fill)
ctext(650,'¿Quieres probar o unirte a DXN?',f('Inter-ExtraBold.otf',54),(255,255,255))
ctext(725,'Café y productos de Ganoderma (Reishi)',f('Inter-SemiBold.otf',36),(170,235,150))
ctext(780,'Bienestar  ·  Salud  ·  Emprendimiento',f('Inter-Medium.otf',32),(230,240,230))
# white card
x0,y0,x1,y1=60,850,W-60,1230
d.rounded_rectangle((x0,y0,x1,y1),radius=36,fill=(255,255,255))
q=qrcode.QRCode(border=1,box_size=10,error_correction=qrcode.constants.ERROR_CORRECT_M)
q.add_data('https://www.dxn2ulatam.com/pws/180143649'); q.make()
qi=q.make_image(fill_color='black',back_color='white').convert('RGB').resize((320,320),Image.NEAREST)
bg.paste(qi,(x0+30,y0+30))
tx=x0+380; dk=(15,60,35); red=(200,30,30)
d.text((tx,y0+40),'Escanea el código',font=f('Inter-ExtraBold.otf',40),fill=dk)
d.text((tx,y0+92),'o entra a mi página:',font=f('Inter-Medium.otf',32),fill=(60,60,60))
d.text((tx,y0+150),'dxn2ulatam.com/',font=f('Inter-Bold.otf',34),fill=red)
d.text((tx,y0+192),'pws/180143649',font=f('Inter-Bold.otf',34),fill=red)
d.rounded_rectangle((tx,y0+262,x1-30,y0+342),radius=40,fill=(37,211,102))
t='WhatsApp 951 228 0679'; fo=f('Inter-Bold.otf',32)
w=d.textlength(t,font=fo); d.text((tx+((x1-30-tx)-w)/2,y0+282),t,font=fo,fill=(255,255,255))
ctext(1255,'Roque Hernández · Distribuidor DXN · Código 180143649',f('Inter-SemiBold.otf',28),(255,255,255))
ctext(1300,'Suplemento alimenticio. No sustituye tratamiento médico.',f('Inter-Medium.otf',22),(190,210,195))
bg.save(B+'out/publicacion_dxn.jpg','JPEG',quality=92)
