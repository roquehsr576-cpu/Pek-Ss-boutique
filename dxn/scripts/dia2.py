import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/scripts')
from engine import *
D='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/dia2/'
B='/tmp/claude-0/-home-user-Pek-Ss-boutique/f5892703-9636-54fe-89dd-0efcb8a15e5f/'
which=sys.argv[1]
if which=='formas':
    names=['higado','corazon','cerebro','pavo','kimshen','ruyi']
    ims=[Image.open(D+f'f_{n}.png').convert('RGB') for n in names]
    # 2x3 grid
    g=Image.new('RGB',(W,H),(10,20,12)); cw,ch=W//2,H//3
    for i,im in enumerate(ims):
        r=max(cw/im.width,ch/im.height); t=im.resize((int(im.width*r)+1,int(im.height*r)+1))
        x=(t.width-cw)//2; y=(t.height-ch)//2; g.paste(t.crop((x,y,x+cw,y+ch)),((i%2)*cw,(i//2)*ch))
    d=ImageDraw.Draw(g)
    for i in range(1,2): d.line((i*cw,0,i*cw,H),fill=(0,0,0),width=6)
    for j in range(1,3): d.line((0,j*ch,W,j*ch),fill=(0,0,0),width=6)
    g.save(D+'grid.png'); grid=load_still(D+'grid.png')
    st={n:load_still(D+f'f_{n}.png') for n in names}
    cuts=[10.6,11.5,12.5,13.5,14.6,15.45,16.4]
    segs=[(0,4.4,'clip',Clip(D+'hook_corazon.mp4'),0,0),(4.4,10.6,'still',grid,1.0,1.12)]
    lab=['HÍGADO','CORAZÓN','CEREBRO','PAVO REAL','KIMSHEN','RUYI']
    tx=[(0,2.3,'big','¿SABÍAS QUE\nESTE HONGO...',300),(2.3,4.4,'big','...CRECE CON FORMA\nDE CORAZÓN?',300),
        (4.4,6.6,'big','Y NO ES\nEL ÚNICO',300),(6.6,10.6,'mid','6 FORMAS\nCON NOMBRE\nPROPIO',300)]
    for i,n in enumerate(names):
        segs.append((cuts[i],cuts[i+1],'still',st[n],1.08,1.0)); tx.append((cuts[i],cuts[i+1],'pill',f'{i+1} · {lab[i]}',330))
    segs.append((16.4,20.6,'still',grid,1.12,1.0))
    tx+= [(16.4,18.0,'big','¿CUÁL TE\nSORPRENDIÓ\nMÁS?',620),(18.0,20.6,'big','¿Y POR QUÉ?\nCUÉNTAME',660),(18.3,20.6,'small','Las formas, según DXN',900)]
    render(D+'v_formas.mp4',20.6,segs,tx,flashes=[4.4]+cuts[:-1]+[16.4],dark_from=16.4)
elif which=='frappe':
    segs=[(0,3.0,'clip',Clip(D+'hook_frappe.mp4'),0,0),(3.0,6.2,'still',load_still(D+'r_ingred.png'),1.0,1.1),
          (6.2,8.4,'still',load_still(D+'r_licua.png'),1.12,1.0),(8.4,10.4,'clip',Clip(D+'hook_frappe.mp4',3.0),0,0),
          (10.4,16.0,'still',load_still(D+'r_final.png'),1.0,1.12)]
    tx=[(0,3.0,'big','FRAPPÉ DE\nGANODERMA',280),(0.5,3.0,'pill','EN 30 SEGUNDOS',560),
        (3.0,6.2,'pill','NECESITAS',260),(3.2,6.2,'small','1 sobre de café de Ganoderma\n½ taza de leche fría\n1 taza de hielo\nCrema y chocolate (opcional)',400),
        (6.2,8.4,'pill','LICÚA 30 SEGUNDOS',300),(8.4,10.4,'pill','SIRVE Y DECORA',300),
        (10.4,12.6,'huge','¡LISTO!',300),(12.6,16.0,'big','GUÁRDALO\nPARA DESPUÉS',260),(13.0,16.0,'small','Pide tu café: escríbeme "FRAPPÉ"',540)]
    render(D+'v_frappe.mp4',16.0,segs,tx,flashes=[3.0,6.2,8.4,10.4])
elif which=='socio':
    segs=[(0,4.0,'clip',Clip(B+'reel3/hook.mp4'),0,0),(4.0,9.1,'still',load_still(B+'images/8.webp',fit=True),1.0,1.08),
          (9.1,12.0,'still',load_still(D+'o_cel.png'),1.0,1.12),(12.0,14.9,'still',load_still(B+'reel2/s4.png'),1.0,1.15),
          (14.9,19.3,'still',load_still(D+'perfil.jpg',fit=True),1.0,1.06),(19.3,23.6,'still',load_still(B+'reel3/stir.mp4'.replace('stir.mp4','powder.png')),1.05,1.0)]
    tx=[(0,2.0,'big','¿TOMAS CAFÉ\nTODOS LOS DÍAS?',300),(2.0,4.0,'pill','ESTO TE INTERESA',340),
        (4.0,9.1,'big','PRECIO DE\nDISTRIBUIDOR',260),(4.4,9.1,'small','en tu café de Ganoderma DXN',490),
        (9.1,12.0,'big','REGISTRO\nEN LÍNEA',300),(9.4,12.0,'pill','EN MINUTOS',540),
        (12.0,14.9,'mid','UNA MEMBRESÍA\nVÁLIDA EN TODO\nEL MUNDO',260),
        (14.9,19.3,'pill','SOY ROQUE · DISTRIBUIDOR DXN',230),(15.3,19.3,'small','Te ayudo paso a paso',1560),
        (19.3,23.6,'mid','ESCRÍBEME',560),(19.3,23.6,'huge','"SOCIO"',650),(19.8,23.6,'small','y te paso mi enlace',850)]
    render(D+'v_socio.mp4',23.6,segs,tx,flashes=[4.0,9.1,12.0,14.9,19.3],dark_from=19.3)
print('ok',which)
