import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
P='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/carrusel/prod/'
for k in ['black','cream','lite','zhino','mocha','cocozhi','roasted','tealatte','lemonzhi']:
    im=Image.open(P+k+'.jpg').convert('RGB'); w,h=im.size
    # mask of 'near white' connected to borders via flood fill on a copy
    m=im.copy(); 
    for seed in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(w//2,h-1),(0,h//2),(w-1,h//2)]:
        if sum(m.getpixel(seed))>700: ImageDraw.floodfill(m,seed,(255,0,255),thresh=28)
    px=m.load(); a=Image.new('L',(w,h),255); ap=a.load()
    for y in range(h):
        for x in range(w):
            if px[x,y]==(255,0,255): ap[x,y]=0
    a=a.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    rgba=im.convert('RGBA'); rgba.putalpha(a)
    bb=a.point(lambda v:255 if v>20 else 0).getbbox(); rgba=rgba.crop(bb)
    rgba.save(P+k+'.png'); print(k,rgba.size)
