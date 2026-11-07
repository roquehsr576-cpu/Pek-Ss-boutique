from PIL import Image, ImageDraw, ImageFilter, ImageFont
B='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
W,H=1640,924
src=Image.open(B+'images/8.webp').convert('RGB'); print(src.size)
bh=round(src.height*W/src.width)
ban=src.resize((W,bh),Image.LANCZOS)
# background: stretched + blurred banner to fill mobile bands
top=(H-bh)//2
bg=Image.new('RGB',(W,H),(12,52,30))
g=ImageDraw.Draw(bg)
for y in range(H):
    k=abs(y-H/2)/(H/2); c=(int(16-8*k),int(70-30*k),int(38-16*k)); g.line((0,y,W,y),fill=c)
bg.paste(ban,(0,top))
# feather banner edges into green
for i in range(24):
    a=int(200*(1-i/24))
    ov=Image.new('RGBA',(W,1),(12,52,30,a))
    bg.paste(ov,(0,top+i),ov); bg.paste(ov,(0,top+bh-1-i),ov)
# soft fade edges of banner into bands
fade=40
for i in range(fade):
    a=int(255*(1-i/fade))
    strip=bg.crop((0,top-fade+i,W,top-fade+i+1))
for y0 in (top, top+bh):
    pass
d=ImageDraw.Draw(bg,'RGBA')
F='/usr/share/fonts/opentype/inter/'
fo=ImageFont.truetype(F+'Inter-Bold.otf',30)
t='Pedidos y registro:   WhatsApp 951 228 0679   ·   dxn2ulatam.com/pws/180143649'
w=d.textlength(t,font=fo)
ry=top+bh-78
d.rounded_rectangle(((W-w)/2-34,ry,(W+w)/2+34,ry+58),radius=29,fill=(10,60,30,215))
d.text(((W-w)/2,ry+12),t,font=fo,fill=(255,255,255))
Fm=ImageFont.truetype(F+'Inter-SemiBold.otf',34)
t2='Roque Hernández  ·  Distribuidor independiente DXN  ·  Código 180143649'
w2=d.textlength(t2,font=Fm); d.text(((W-w2)/2,(top-34)/2-4),t2,font=Fm,fill=(200,240,190))
bg.save(B+'out/portada_facebook_dxn.jpg','JPEG',quality=93)
print(top,bh,ry)
# previews of crops
dk=bg.crop((0,(H-607)//2,W,(H-607)//2+607)); dk.save(B+'scratchpad/prev_desktop.jpg')
